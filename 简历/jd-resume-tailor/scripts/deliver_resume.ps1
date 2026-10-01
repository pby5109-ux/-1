[CmdletBinding()]
param(
    [switch]$InspectDesktop,
    [string[]]$SourceFiles,
    [string]$DestinationDirectory,
    [switch]$Copy
)
$ErrorActionPreference = 'Stop'
if ($InspectDesktop) {
    $desktop = [Environment]::GetFolderPath('DesktopDirectory')
    $regDesktop = $null
    if (Test-Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders') {
        $regDesktop = (Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders' -Name Desktop -ErrorAction SilentlyContinue).Desktop
        if ($regDesktop) { $regDesktop = [Environment]::ExpandEnvironmentVariables($regDesktop) }
    }
    [pscustomobject]@{systemDesktop=$desktop;registryDesktop=$regDesktop;exists=([bool]$desktop -and (Test-Path -LiteralPath $desktop))} | ConvertTo-Json
    return
}
if (-not $SourceFiles -or -not $DestinationDirectory) { throw 'Provide SourceFiles and an explicit DestinationDirectory.' }
$destination = [IO.Path]::GetFullPath($DestinationDirectory)
if (-not (Test-Path -LiteralPath $destination -PathType Container)) { throw "Destination directory does not exist: $destination" }
$seen = @{}
$plan = @(foreach ($source in $SourceFiles) {
    $item = Get-Item -LiteralPath $source
    if ($item.PSIsContainer -or $item.Extension -notin @('.docx','.pdf')) { throw "Expected a DOCX or PDF file: $source" }
    $target = Join-Path $destination $item.Name
    if ($seen.ContainsKey($target)) { throw "Duplicate destination filename: $target" }
    $seen[$target] = $true
    $hash = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash
    $reuse = Test-Path -LiteralPath $target
    if ($reuse -and (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $hash) {
        throw "Different content already exists; nothing copied: $target"
    }
    [pscustomobject]@{source=$item.FullName;destination=$target;sha256=$hash;reuse=$reuse;status='planned'}
})
foreach ($entry in $plan) {
    if ($Copy) {
        if (-not $entry.reuse) { [IO.File]::Copy($entry.source, $entry.destination, $false) }
        if ((Get-FileHash -LiteralPath $entry.destination -Algorithm SHA256).Hash -ne $entry.sha256) { throw "Delivery hash mismatch: $($entry.destination)" }
        $entry.status = 'verified'
    }
}
ConvertTo-Json -InputObject $plan -Depth 3
