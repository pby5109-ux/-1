[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ContentPath,

    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory
)

$ErrorActionPreference = 'Stop'
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillRoot = Split-Path -Parent $scriptRoot
$pythonCandidate = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$python = if (Test-Path -LiteralPath $pythonCandidate) {
    (Resolve-Path -LiteralPath $pythonCandidate).Path
} else {
    (Get-Command python.exe -ErrorAction Stop).Source
}

$resolvedContent = (Resolve-Path -LiteralPath $ContentPath).Path
$payload = Get-Content -LiteralPath $resolvedContent -Raw -Encoding UTF8 | ConvertFrom-Json
if ($payload.approved -ne $true -or [string]::IsNullOrWhiteSpace($payload.preview_id)) {
    throw 'Generation is blocked until the exact preview is explicitly approved.'
}

& $python (Join-Path $scriptRoot 'validate_resume_content.py') --content $resolvedContent
if ($LASTEXITCODE -ne 0) {
    throw 'Approved content validation failed.'
}

$resolvedOutput = [System.IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path -LiteralPath $resolvedOutput) {
    throw "Refusing to reuse an existing application directory: $resolvedOutput"
}
New-Item -ItemType Directory -Path $resolvedOutput | Out-Null

$invalid = [System.IO.Path]::GetInvalidFileNameChars()
function Get-SafeName([string]$Value) {
    $result = $Value
    foreach ($character in $invalid) {
        $result = $result.Replace([string]$character, '-')
    }
    return $result.Trim().TrimEnd('.')
}

$baseName = "彭博裕-$(Get-SafeName $payload.company)-$(Get-SafeName $payload.role)-$($payload.date)"
$approvedCopy = Join-Path $resolvedOutput 'approved-content.json'
$docxPath = Join-Path $resolvedOutput "$baseName.docx"
$pdfPath = Join-Path $resolvedOutput "$baseName.pdf"
$renderPath = Join-Path $resolvedOutput "$baseName-preview.png"
Copy-Item -LiteralPath $resolvedContent -Destination $approvedCopy

& $python (Join-Path $scriptRoot 'build_resume.py') --content $approvedCopy --output $docxPath
if ($LASTEXITCODE -ne 0) {
    throw 'DOCX generation failed.'
}

& (Join-Path $scriptRoot 'export_resume.ps1') -DocxPath $docxPath -PdfPath $pdfPath -RenderPath $renderPath
if ($LASTEXITCODE -ne 0) {
    throw 'PDF export or verification failed.'
}

Write-Output "OK: generated approved resume bundle in $resolvedOutput"
