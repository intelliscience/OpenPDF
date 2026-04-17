import fitz
import argparse
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from PIL import Image

class OpenPDF:
    def __init__(self, author=None, creator=None):
        self.copy_text = "OpenPDF 2026-Present copyrights GPL-V3.0 Fjord Enzo Bertrand-Helmgens"
        self.author = author if author else "Fjord Enzo Bertrand-Helmgens"
        self.creator = creator if creator else "OpenPDF Encoder 2026"

    def stamp(self, pdf_path):
        doc = fitz.open(pdf_path)
        meta = doc.metadata
        
        meta["author"] = self.author
        meta["creator"] = self.creator
        meta["producer"] = "OpenPDF Engine 2026 (GPL-V3.0)"
        meta["subject"] = self.copy_text
        
        doc.set_metadata(meta)
        
        for page in doc:
            page.insert_text(
                (50, page.rect.height - 20), 
                self.copy_text, 
                fontsize=7, 
                color=(0.5, 0.5, 0.5)
            )
            
        doc.save(pdf_path, incremental=True, encryption=0)
        doc.close()

    def convert_text(self, src, out):
        doc = SimpleDocTemplate(
            out, 
            pagesize=letter,
            author=self.author,
            creator=self.creator,
            producer="OpenPDF Engine 2026"
        )
        styles = getSampleStyleSheet()
        style = styles["Normal"]
        style.leading = 14
        
        story = []
        with open(src, 'r', encoding='utf-8') as f:
            for line in f:
                clean_line = line.strip()
                if not clean_line:
                    story.append(Spacer(1, 12))
                else:
                    p = Paragraph(clean_line, style)
                    story.append(p)
        
        doc.build(story)
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
    parser = argparse.ArgumentParser(description="OpenPDF Encoder")
    parser.add_argument("--text", help="Input TXT file")
    parser.add_argument("--imgs", nargs="+", help="Input Image files")
    parser.add_argument("--flatten", help="PDF to flatten")
    parser.add_argument("--compress", help="PDF to compress")
    parser.add_argument("--out", required=True, help="Output path")
    parser.add_argument("--author", help="Custom Author Name")
    parser.add_argument("--creator", help="Custom Creator Name")
    
    args = parser.parse_args()
    op = OpenPDF(author=args.author, creator=args.creator)

    try:
        if args.text: op.convert_text(args.text, args.out)
        elif args.imgs: op.convert_imgs(args.imgs, args.out)
        elif args.flatten: op.flatten(args.flatten, args.out)
        elif args.compress: op.compress(args.compress, args.out)
        print(f"[SUCCESS] Generated: {args.out}")
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main()