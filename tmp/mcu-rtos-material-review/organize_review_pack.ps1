[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$ManifestPath,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$DestinationRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-ExistingFilePath {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Label
    )

    if (-not [IO.Path]::IsPathFullyQualified($Path)) {
        throw "$Label must be an absolute filesystem path: $Path"
    }

    $item = Get-Item -LiteralPath $Path -ErrorAction Stop
    if ($item.PSIsContainer) {
        throw "$Label must be a file, not a directory: $Path"
    }
    return $item.FullName
}

function Get-AbsoluteDirectoryPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not [IO.Path]::IsPathFullyQualified($Path)) {
        throw "DestinationRoot must be an absolute filesystem path: $Path"
    }

    $fullPath = [IO.Path]::GetFullPath($Path)
    if (Test-Path -LiteralPath $fullPath) {
        $item = Get-Item -LiteralPath $fullPath -ErrorAction Stop
        if (-not $item.PSIsContainer) {
            throw "DestinationRoot must be a directory: $fullPath"
        }
        return $item.FullName
    }

    return $fullPath
}

function Test-PathWithinRoot {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Root
    )

    $pathFull = [IO.Path]::GetFullPath($Path)
    $rootFull = [IO.Path]::GetFullPath($Root)
    $rootCompare = $rootFull -replace '[\\/]+$', ''
    if ($rootCompare -match '^[A-Za-z]:$') {
        $rootCompare += '\'
    }
    $prefix = if ($rootCompare.EndsWith('\') -or $rootCompare.EndsWith('/')) {
        $rootCompare
    }
    else {
        $rootCompare + '\'
    }

    return $pathFull.Equals($rootCompare, [StringComparison]::OrdinalIgnoreCase) -or
        $pathFull.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)
}

function Get-FileSha256 {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256 -ErrorAction Stop).Hash.ToUpperInvariant()
}

function Get-SafeTargetPath {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$RelativeTarget
    )

    if ([IO.Path]::IsPathFullyQualified($RelativeTarget) -or [IO.Path]::IsPathRooted($RelativeTarget)) {
        throw "relativeTarget must be relative, not rooted: $RelativeTarget"
    }

    $segments = $RelativeTarget -split '[\\/]'
    if ($segments.Count -eq 0 -or @($segments | Where-Object { $_ -eq '..' -or $_ -match ':' }).Count -gt 0) {
        throw "relativeTarget may not contain '..': $RelativeTarget"
    }
    if ([string]::IsNullOrWhiteSpace(($segments -join ''))) {
        throw "relativeTarget must name a file: $RelativeTarget"
    }

    $target = [IO.Path]::GetFullPath([IO.Path]::Combine($Root, $RelativeTarget))
    if (-not (Test-PathWithinRoot -Path $target -Root $Root)) {
        throw "Resolved target escapes DestinationRoot: $RelativeTarget"
    }
    return $target
}

$manifestFile = Get-ExistingFilePath -Path $ManifestPath -Label 'ManifestPath'
$destination = Get-AbsoluteDirectoryPath -Path $DestinationRoot

$rawManifest = Get-Content -LiteralPath $manifestFile -Raw -ErrorAction Stop
$entries = @($rawManifest | ConvertFrom-Json -ErrorAction Stop)
if ($entries.Count -eq 0) {
    throw "Manifest must contain at least one { source, relativeTarget } entry."
}

# Validate every source, resolve every target, and calculate all source hashes before
# creating a destination directory or copying anything. This makes name/SHA conflicts
# fail before any material is written.
$plans = @()
$uniqueByTarget = @{}
foreach ($entry in $entries) {
    if ($null -eq $entry -or
        [string]::IsNullOrWhiteSpace([string]$entry.source) -or
        [string]::IsNullOrWhiteSpace([string]$entry.relativeTarget)) {
        throw 'Every manifest entry must contain non-empty source and relativeTarget strings.'
    }

    $source = Get-ExistingFilePath -Path ([string]$entry.source) -Label 'source'
    $target = Get-SafeTargetPath -Root $destination -RelativeTarget ([string]$entry.relativeTarget)
    $sourceInfo = Get-Item -LiteralPath $source -ErrorAction Stop
    $sourceHash = Get-FileSha256 -Path $source

    $plan = [pscustomobject]@{
        Source       = $source
        Target       = $target
        SourceSize   = [int64]$sourceInfo.Length
        SourceHash   = $sourceHash
        Status       = 'pending-copy'
        TargetSize   = [int64]0
        TargetHash   = $null
        UniquePlan   = $null
    }

    if ($uniqueByTarget.ContainsKey($target)) {
        $existing = $uniqueByTarget[$target]
        if ($existing.SourceHash -ne $sourceHash) {
            throw "Target has multiple sources with different SHA256 values; refusing to overwrite: $target"
        }
        $plan.Status = 'reused'
        $plan.UniquePlan = $existing
        $plans += $plan
        continue
    }

    $parent = [IO.Path]::GetDirectoryName($target)
    $check = $target
    while ($check) {
        if (Test-Path -LiteralPath $check) {
            if ((Get-Item -LiteralPath $check).Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "Refusing redirected target or ancestor: $check"
            }
        }
        $check = [IO.Path]::GetDirectoryName($check)
    }
    if (Test-Path -LiteralPath $parent) {
        $parentInfo = Get-Item -LiteralPath $parent -ErrorAction Stop
        if (-not $parentInfo.PSIsContainer) {
            throw "Target parent is a file, not a directory: $parent"
        }
    }

    if (Test-Path -LiteralPath $target) {
        $targetInfo = Get-Item -LiteralPath $target -ErrorAction Stop
        if ($targetInfo.PSIsContainer) {
            throw "Target is a directory, not a file: $target"
        }
        $targetHash = Get-FileSha256 -Path $target
        if ($targetHash -ne $sourceHash) {
            throw "Same target name exists with a different SHA256; refusing to overwrite: $target"
        }
        $plan.Status = 'reused'
        $plan.TargetSize = [int64]$targetInfo.Length
        $plan.TargetHash = $targetHash
    }

    $uniqueByTarget[$target] = $plan
    $plans += $plan
}

# Only now create missing directories. File.Copy with overwrite=false refuses
# an existing target even if it appears between the existence check and copy.
foreach ($plan in $uniqueByTarget.Values) {
    if ($plan.Status -eq 'pending-copy') {
        $parent = [IO.Path]::GetDirectoryName($plan.Target)
        if (-not (Test-Path -LiteralPath $parent)) {
            New-Item -ItemType Directory -Path $parent -Force | Out-Null
        }

        if (Test-Path -LiteralPath $plan.Target) {
            $raceInfo = Get-Item -LiteralPath $plan.Target -ErrorAction Stop
            if ($raceInfo.PSIsContainer) {
                throw "Target appeared as a directory during copy: $($plan.Target)"
            }
            $raceHash = Get-FileSha256 -Path $plan.Target
            if ($raceHash -ne $plan.SourceHash) {
                throw "Target appeared with a different SHA256 during copy; refusing to overwrite: $($plan.Target)"
            }
            $plan.Status = 'reused'
        }
        else {
            [IO.File]::Copy($plan.Source, $plan.Target, $false)
            $plan.Status = 'copied'
        }
    }

    $resultInfo = Get-Item -LiteralPath $plan.Target -ErrorAction Stop
    if ($resultInfo.PSIsContainer) {
        throw "Target is not a file after operation: $($plan.Target)"
    }
    $resultHash = Get-FileSha256 -Path $plan.Target
    if ($resultHash -ne $plan.SourceHash) {
        throw "SHA256 verification failed after operation: $($plan.Target)"
    }
    $plan.TargetSize = [int64]$resultInfo.Length
    $plan.TargetHash = $resultHash
}

$output = foreach ($plan in $plans) {
    $base = if ($null -ne $plan.UniquePlan) { $plan.UniquePlan } else { $plan }
    [pscustomobject]@{
        source = $plan.Source
        target = $plan.Target
        size   = [int64]$base.TargetSize
        hash   = [string]$base.TargetHash
        status = [string]$base.Status
    }
}

@($output) | ConvertTo-Json -Depth 4
