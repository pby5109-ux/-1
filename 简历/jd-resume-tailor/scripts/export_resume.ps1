[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$DocxPath,

    [Parameter(Mandatory = $true)]
    [string]$PdfPath,

    [string]$RenderPath,
    [string]$PdfInfoPath,
    [string]$PdfToPpmPath
)

$ErrorActionPreference = 'Stop'

function Resolve-PopplerTool {
    param(
        [Parameter(Mandatory = $true)][string]$ToolName,
        [string]$ExplicitPath
    )

    if ($ExplicitPath) {
        $resolved = (Resolve-Path -LiteralPath $ExplicitPath).Path
        return $resolved
    }

    $command = Get-Command "$ToolName.exe" -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $profileRoot = [Environment]::GetFolderPath('UserProfile')
    $bundled = Join-Path $profileRoot ".cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\$ToolName.exe"
    if (Test-Path -LiteralPath $bundled) {
        return (Resolve-Path -LiteralPath $bundled).Path
    }

    throw "Cannot locate $ToolName.exe. Pass its path explicitly."
}

$resolvedDocx = (Resolve-Path -LiteralPath $DocxPath).Path
$resolvedPdf = [System.IO.Path]::GetFullPath($PdfPath)
if ([System.IO.Path]::GetExtension($resolvedDocx) -ne '.docx') {
    throw "Input must be a DOCX file: $resolvedDocx"
}
if ([System.IO.Path]::GetExtension($resolvedPdf) -ne '.pdf') {
    throw "Output must be a PDF file: $resolvedPdf"
}
if (Test-Path -LiteralPath $resolvedPdf) {
    throw "Refusing to overwrite existing PDF: $resolvedPdf"
}

$pdfParent = Split-Path -Parent $resolvedPdf
if (-not (Test-Path -LiteralPath $pdfParent)) {
    New-Item -ItemType Directory -Path $pdfParent | Out-Null
}

if (-not $RenderPath) {
    $RenderPath = [System.IO.Path]::ChangeExtension($resolvedPdf, '.png')
}
$resolvedRender = [System.IO.Path]::GetFullPath($RenderPath)
if ([System.IO.Path]::GetExtension($resolvedRender) -ne '.png') {
    throw "Render output must be a PNG file: $resolvedRender"
}
if (Test-Path -LiteralPath $resolvedRender) {
    throw "Refusing to overwrite existing render: $resolvedRender"
}

$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($resolvedDocx, $false, $true)
    # 17 = wdExportFormatPDF; 0 = print optimized; 0 = all document.
    $document.ExportAsFixedFormat($resolvedPdf, 17, $false, 0, 0)
}
finally {
    if ($document) {
        $document.Close($false)
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($document)
    }
    if ($word) {
        $word.Quit()
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

if (-not (Test-Path -LiteralPath $resolvedPdf)) {
    throw "Word did not create the expected PDF: $resolvedPdf"
}

$pdfInfo = Resolve-PopplerTool -ToolName 'pdfinfo' -ExplicitPath $PdfInfoPath
$pdfToPpm = Resolve-PopplerTool -ToolName 'pdftoppm' -ExplicitPath $PdfToPpmPath
$info = & $pdfInfo $resolvedPdf 2>&1 | Out-String
if ($LASTEXITCODE -ne 0) {
    throw "pdfinfo failed:`n$info"
}

$pageMatch = [regex]::Match($info, '(?m)^Pages:\s+(\d+)\s*$')
if (-not $pageMatch.Success -or [int]$pageMatch.Groups[1].Value -ne 1) {
    throw "Resume PDF must contain exactly one page.`n$info"
}

$sizeMatch = [regex]::Match($info, '(?m)^Page size:\s+([\d.]+)\s+x\s+([\d.]+)\s+pts')
if (-not $sizeMatch.Success) {
    throw "Could not read PDF page size.`n$info"
}
$width = [double]$sizeMatch.Groups[1].Value
$height = [double]$sizeMatch.Groups[2].Value
if ([math]::Abs($width - 595.28) -gt 2.0 -or [math]::Abs($height - 841.89) -gt 2.0) {
    throw "Resume PDF is not A4: ${width} x ${height} pt"
}

$renderBase = [System.IO.Path]::Combine(
    [System.IO.Path]::GetDirectoryName($resolvedRender),
    [System.IO.Path]::GetFileNameWithoutExtension($resolvedRender)
)
& $pdfToPpm -f 1 -singlefile -r 160 -png $resolvedPdf $renderBase 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $resolvedRender)) {
    throw "PDF rendering failed: $resolvedRender"
}

Write-Output "OK: exported one-page A4 PDF: $resolvedPdf"
Write-Output "OK: rendered visual-review PNG: $resolvedRender"
