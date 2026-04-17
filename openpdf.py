import fitz
import argparse
import os
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image

class OpenPDF:
    def __init__(self):
        self.copy_text = "OpenPDF 2026-Present copyrights GPL-V3.0 Fjord Enzo Bertrand-Helmgens"

    def stamp(self, pdf_path):
        """Internal helper to apply the mandatory watermark and metadata."""
        doc = fitz.open(pdf_path)
        meta = doc.metadata
        meta["author"] = "Fjord Enzo Bertrand-Helmgens"
        meta["creator"] = "OpenPDF 2026"
        doc.set_metadata(meta)
        for page in doc:
            page.insert_text((20, page.rect.height - 20), self.copy_text, fontsize=7, color=(0.5, 0.5, 0.5))
        doc.save(pdf_path, incremental=True, encryption=0)
        doc.close()

    def convert_text(self, src, out):
        c = canvas.Canvas(out, pagesize=letter)
        y = 750
        with open(src, 'r') as f:
            for line in f:
                if y < 50: 
                    c.showPage()
                    y = 750
                c.drawString(50, y, line.strip())
                y -= 15
        c.save()
        self.stamp(out)

    def convert_imgs(self, srcs, out):
        imgs = [Image.open(i).convert("RGB") for i in srcs]
        imgs[0].save(out, save_all=True, append_images=imgs[1:])
        self.stamp(out)
    
    def flatten(self, src, out):
        doc = fitz.open(src)
        res = fitz.open()
        for page in doc:
            pix = page.get_pixmap(dpi=150)
            new_pg = res.new_page(width=page.rect.width, height=page.rect.height)
            new_pg.insert_image(page.rect, pixmap=pix)
        res.save(out)
        res.close()
        self.stamp(out)

    def compress(self, src, out):
        doc = fitz.open(src)
        doc.save(out, garbage=4, deflate=True)
        doc.close()
        self.stamp(out)

def main():
    parser = argparse.ArgumentParser(description="OpenPDF - 2026 ")
    parser.add_argument("--text", help="Input TXT")
    parser.add_argument("--imgs", nargs="+", help="Input Images")
    parser.add_argument("--flatten", help="Input PDF to flatten")
    parser.add_argument("--compress", help="Input PDF to compress")
    parser.add_argument("--out", required=True, help="Output path")

    args = parser.parse_args()
    op = OpenPDF()

    if args.text: op.convert_text(args.text, args.out)
    elif args.imgs: op.convert_imgs(args.imgs, args.out)
    elif args.flatten: op.flatten(args.flatten, args.out)
    elif args.compress: op.compress(args.compress, args.out)
    print(f"[Success] Created: {args.out}")

if __name__ == "__main__":
    main()