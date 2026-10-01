<#
Cooperative workspace category locks. No automatic stale-lock takeover.
Acquire returns a token; Release requires the same owner and token.
Run from any directory; paths are fixed relative to this script.
#>
[CmdletBinding()]
param(
    [ValidateSet('Status','Acquire','Release')][string]$Action = 'Status',
    [ValidateSet('workspace-governance','memory','training','knowledge','question-bank','resume')][string]$Category,
    [string]$Owner,
    [string]$Task,
    [string]$Token
)
$ErrorActionPreference = 'Stop'
$rootPath = Split-Path -Parent $PSScriptRoot
$lockDirectory = Join-Path $rootPath '.workspace-locks'
if (-not (Test-Path -LiteralPath $lockDirectory)) {
    [void][IO.Directory]::CreateDirectory($lockDirectory)
}
if ((Get-Item -LiteralPath $lockDirectory).Attributes -band [IO.FileAttributes]::ReparsePoint) {
    throw 'Refusing a redirected lock directory.'
}
if ($Action -eq 'Status') {
    $rows = @(Get-ChildItem -LiteralPath $lockDirectory -File | ForEach-Object {
        if ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Redirected lock file.' }
        try {
            $data = Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
            $started = [DateTimeOffset]::Parse($data.started)
            [pscustomobject]@{category=$_.BaseName;owner=$data.owner;task=$data.task;started=$data.started;ageMinutes=[math]::Round(([DateTimeOffset]::Now-$started).TotalMinutes,1)}
        } catch {
            [pscustomobject]@{category=$_.BaseName;error='Unreadable lock: do not overwrite or delete.'}
        }
    })
    ConvertTo-Json -InputObject $rows -Depth 4
    return
}
if (-not $Category -or [string]::IsNullOrWhiteSpace($Owner)) { throw 'Category and exact task/thread Owner are required.' }
if ($Owner -in @('current-chat','agent','unknown')) { throw 'Use the actual task/thread identifier, not a generic owner.' }
$lockPath = Join-Path $lockDirectory ($Category + '.lock')
if ($Action -eq 'Acquire') {
    if ([string]::IsNullOrWhiteSpace($Task)) { throw 'A specific Task description is required.' }
    $payload = [ordered]@{owner=$Owner;task=$Task;started=[DateTimeOffset]::Now.ToString('o');token=[guid]::NewGuid().ToString()}
    # CreateNew is atomic and fails even when the existing file is empty.
    $stream = [IO.File]::Open($lockPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    try {
        $bytes = [Text.Encoding]::UTF8.GetBytes(($payload | ConvertTo-Json -Compress))
        $stream.Write($bytes,0,$bytes.Length)
        $stream.Flush()
    } finally { $stream.Dispose() }
    $payload | ConvertTo-Json -Compress
    return
}
if ([string]::IsNullOrWhiteSpace($Token)) { throw 'The token returned by Acquire is required.' }
if ((Get-Item -LiteralPath $lockPath).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Refusing a redirected lock file.' }
$lockData = Get-Content -LiteralPath $lockPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($lockData.owner -cne $Owner -or $lockData.token -cne $Token) { throw 'Owner/token mismatch: lock kept unchanged.' }
Remove-Item -LiteralPath $lockPath
[pscustomobject]@{released=$Category;owner=$Owner} | ConvertTo-Json -Compress
