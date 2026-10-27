<# Read-only inventory and local Markdown/HTML link check. Does not write or delete. #>
[CmdletBinding()]
param(
    [ValidateSet('Navigation','All')][string]$Scope = 'Navigation'
)
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$prefix = $root.TrimEnd('\','/') + [IO.Path]::DirectorySeparatorChar
$excludedNames = @('.git','.workspace-locks','node_modules','packages','__pycache__')
$files = [Collections.Generic.List[IO.FileInfo]]::new()
$skipped = [Collections.Generic.List[string]]::new()
$stack = [Collections.Generic.Stack[string]]::new()
$stack.Push($root)
while ($stack.Count -gt 0) {
    $directory = $stack.Pop()
    foreach ($item in Get-ChildItem -LiteralPath $directory -Force) {
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            $skipped.Add($item.FullName.Substring($prefix.Length))
            continue
        }
        if ($item.PSIsContainer) {
            if ($item.FullName -ne $root -and (Test-Path -LiteralPath (Join-Path $item.FullName '.git'))) {
                $skipped.Add($item.FullName.Substring($prefix.Length))
            } elseif ($item.Name -notin $excludedNames) {
                $stack.Push($item.FullName)
            }
        } else {
            $files.Add($item)
        }
    }
}
$navigation = @('README.md','AGENTS.md','RESOURCES.md','MISSION.md','NOTES.md',
    '记忆与产物\00-项目接续记忆.md','项目集合\电赛视觉加灰度\学习\00-学习入口与诊断断点.md')
$documents = @($files | Where-Object {
    $rel = $_.FullName.Substring($prefix.Length)
    $eligible = $rel -notmatch '^(tmp|记忆与产物\\99-历史归档)\\'
    if ($Scope -eq 'Navigation') {
        $eligible -and ($_.Name -eq 'README.md' -or $rel -in $navigation)
    } else {
        $eligible -and $_.Extension -in @('.md','.html')
    }
})
$missing = [Collections.Generic.List[object]]::new()
$external = 0
$checked = 0
# Supports spaces/parentheses in angle destinations and balanced filename parentheses.
$mdPattern = '\[[^\]\r\n]*\]\((?<target><[^>\r\n]+>|(?:[^()\r\n]|\((?:[^()\r\n]|\([^()\r\n]*\))*\))+)\)'
foreach ($document in $documents) {
    $body = Get-Content -LiteralPath $document.FullName -Raw -Encoding UTF8
    $body = [regex]::Replace($body, '(?ms)^\s*(`{3,}|~{3,}).*?^\s*\1[^\r\n]*$', {
        param($m) [regex]::Replace($m.Value, '[^\r\n]', ' ')
    })
    $matches = if ($document.Extension -eq '.html') {
        [regex]::Matches($body, '(?:href|src)\s*=\s*["''](?<target>[^"'']+)["'']', 'IgnoreCase')
    } else { [regex]::Matches($body, $mdPattern) }
    foreach ($match in $matches) {
        $target = $match.Groups['target'].Value.Trim()
        if ($target.StartsWith('<')) { $target = $target.Trim('<','>') }
        else { $target = [regex]::Replace($target, '\s+["''][^"'']*["'']\s*$', '') }
        if ($target -match '^(https?:|mailto:|data:|codex:|plugin:|app:|javascript:|tel:|//)') { continue }
        if ($target.StartsWith('#') -or [string]::IsNullOrWhiteSpace($target)) { continue }
        $pathPart = [Uri]::UnescapeDataString(($target -split '[#?]',2)[0])
        # Codex file links may end in :line or :line:column; not part of the filename.
        $pathPart = [regex]::Replace($pathPart, ':\d+(?::\d+)?$', '')
        if ($pathPart -match '^file:') { $pathPart = ([Uri]$pathPart).LocalPath }
        $pathPart = $pathPart.Replace('/',[IO.Path]::DirectorySeparatorChar)
        if (-not [IO.Path]::IsPathRooted($pathPart)) {
            $pathPart = Join-Path $document.DirectoryName $pathPart
        }
        try { $resolved = [IO.Path]::GetFullPath($pathPart) }
        catch { $resolved = $pathPart }
        if (-not $resolved.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)) {
            $external++
            continue
        }
        $checked++
        if (-not (Test-Path -LiteralPath $resolved)) {
            $line = 1 + [regex]::Matches($body.Substring(0,$match.Index), '\n').Count
            $missing.Add([pscustomobject]@{
                source=$document.FullName.Substring($prefix.Length).Replace('\','/')
                line=$line; target=$target; resolved=$resolved
            })
        }
    }
}
$inventory = @($files | Group-Object { ($_.FullName.Substring($prefix.Length) -split '[\\/]')[0] } |
    ForEach-Object { [pscustomobject]@{
        name=$_.Name; files=$_.Count; bytes=[long](($_.Group | Measure-Object Length -Sum).Sum)
    }} | Sort-Object name)
$rootGit = & git -C $root rev-parse --show-toplevel 2>$null
$hasGit = $LASTEXITCODE -eq 0 -and ([IO.Path]::GetFullPath($rootGit)) -eq $root
$git = if ($hasGit) { [ordered]@{
    branch=(& git -C $root branch --show-current)
    head=(& git -C $root rev-parse --short HEAD)
    status=@(& git -C $root -c core.quotepath=false status --short)
    gitlinks=@(& git -C $root -c core.quotepath=false ls-files --stage | Select-String '^160000 ' | ForEach-Object { $_.Line })
    has_gitmodules=(Test-Path -LiteralPath (Join-Path $root '.gitmodules'))
}} else { $null }
[ordered]@{
    schema_version=1; scope=$Scope; workspace=$root
    observed_at=[DateTimeOffset]::Now.ToString('o')
    coverage='File destinations only; no network requests, no Markdown fragment or teaching-content validation. tmp/archive, packages, Git internals, junctions and nested repositories are excluded.'
    documents_checked=$documents.Count; local_links_checked=$checked
    out_of_workspace_links_not_checked=$external
    missing_links=@($missing); skipped_boundaries=@($skipped)
    inventory=$inventory; git=$git
} | ConvertTo-Json -Depth 8
