"""从本地原理图重建相关页预览；输出可重建，原始 PDF 不修改。"""
from pathlib import Path
import pypdfium2 as pdfium

root = Path(__file__).resolve().parents[1]
source = next((root / '【1】原理图').glob('*.pdf'))
doc = pdfium.PdfDocument(str(source))
for page in (7, 14):
    doc[page - 1].render(scale=1.8).to_pil().save(
        Path(__file__).parent / f'原理图-p{page}.png'
    )
