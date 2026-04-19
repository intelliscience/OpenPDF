import argparse
import os
import datetime
import sys
import io
import platform

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("[CRITICAL] Dependency pypdf not found.")
    print("[ACTION] Run: pip install pypdf --break-system-packages")
    sys.exit(1)

class PDFObjectRegistry:
    def __init__(self):
        self.objects = []
        self.offsets = []

    def register(self, content):
        obj_id = len(self.objects) + 1
        formatted = f"{obj_id} 0 obj\n{content}\nendobj\n".encode()
        self.objects.append(formatted)
        return obj_id

    def register_binary(self, binary_data):
        obj_id = len(self.objects) + 1
        self.objects.append(binary_data)
        return obj_id

class OpenPDFEngine:
    def __init__(self, author=None, title=None, password=None):
        self.author = author or "Project Contributor"
        self.title = title or "OpenPDF Project 2026"
        self.password = password
        self.creator = "OpenPDF Encoder 2026"
        self.producer = "OpenPDF v1.0"
        self.license = "GPL-V3.0 | OpenPDF 2026 System"
        self.date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        
        self.page_width = 612
        self.page_height = 792
        self.margin_left = 50
        self.margin_top = 710
        self.leading = 13
        
        self.registry = PDFObjectRegistry()
        self.pages_data = []

    def _generate_structure(self, content_parts):
        self.registry.register("<< /Type /Catalog /Pages 2 0 R >>")
        
        page_tree_idx = 1
        self.registry.register("") 

        info_dict = (
            f"<< /Title ({self.title}) "
            f"/Author ({self.author}) "
            f"/Creator ({self.creator}) "
            f"/Producer ({self.producer}) "
            f"/CreationDate (D:{self.date}) >>"
        )
        self.registry.register(info_dict)
        
        self.registry.register("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        font_id = 4

        kids_ids = []
        next_id = 5
        for i, text_block in enumerate(content_parts):
            kids_ids.append(next_id)
            
            p_dict = (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {self.page_width} {self.page_height}] "
                f"/Contents {next_id + 1} 0 R "
                f"/Resources << /Font << /F1 {font_id} 0 R >> >> >>"
            )
            self.registry.register(p_dict)
            
            p_footer = f"BT /F1 8 Tf 50 25 Td ({self.license} | Page {i+1}) Tj ET"
            stream_content = (
                f"BT /F1 11 Tf {self.margin_left} {self.margin_top} Td {self.leading} TL\n"
                f"{text_block}\n"
                f"ET\n{p_footer}"
            ).encode()
            
            stream_obj = (
                f"{next_id + 1} 0 obj\n<< /Length {len(stream_content)} >>\n".encode() + 
                b"stream\n" + stream_content + b"\nendstream\nendobj\n"
            )
            self.registry.register_binary(stream_obj)
            next_id += 2

        kids_str = " ".join([f"{k} 0 R" for k in kids_ids])
        page_tree = f"<< /Type /Pages /Kids [{kids_str}] /Count {len(kids_ids)} >>"
        self.registry.objects[page_tree_idx] = f"2 0 obj\n{page_tree}\nendobj\n".encode()

        pdf_stream = [b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"]
        offsets = []
        
        for obj in self.registry.objects:
            offsets.append(sum(len(x) for x in pdf_stream))
            pdf_stream.append(obj)
            
        start_xref = sum(len(x) for x in pdf_stream)
        
        pdf_stream.append(f"xref\n0 {len(self.registry.objects) + 1}\n0000000000 65535 f \n".encode())
        for offset in offsets:
            pdf_stream.append(f"{offset:010} 00000 n \n".encode())
            
        trailer = (
            f"trailer\n<< /Size {len(self.registry.objects) + 1} "
            f"/Root 1 0 R /Info 3 0 R >>\n"
            f"startxref\n{start_xref}\n%%EOF"
        )
        pdf_stream.append(trailer.encode())
        
        return b"".join(pdf_stream)

    def _apply_encryption(self, raw_bytes):
        in_buf = io.BytesIO(raw_bytes)
        reader = PdfReader(in_buf)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.add_metadata({
            "/Title": self.title,
            "/Author": self.author,
            "/Creator": self.creator,
            "/Producer": self.producer
        })

        writer.encrypt(user_password=self.password, owner_password=None, use_128bit=True)

        out_buf = io.BytesIO()
        writer.write(out_buf)
        return out_buf.getvalue()

    def process_file(self, input_path, output_path):
        if not os.path.exists(input_path):
            print(f"[ERROR] Cannot find input: {input_path}")
            sys.exit(1)

        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        current_page_text = ""
        line_count = 0
        
        for line in lines:
            clean_line = line.strip().replace('(', '\\(').replace(')', '\\)')
            chunks = [clean_line[i:i+90] for i in range(0, len(clean_line), 90)]
            if not chunks:
                chunks = [""]

            for chunk in chunks:
                current_page_text += f"({chunk}) Tj T*\n"
                line_count += 1
                if line_count >= 52:
                    self.pages_data.append(current_page_text)
                    current_page_text = ""
                    line_count = 0
        
        if current_page_text:
            self.pages_data.append(current_page_text)

        print(f"[*] Building document structure for {len(self.pages_data)} pages...")
        final_data = self._generate_structure(self.pages_data)
        
        if self.password:
            print("[*] Encrypting byte stream...")
            final_data = self._apply_encryption(final_data)
            
        with open(output_path, 'wb') as f:
            f.write(final_data)

def display_header():
    print("=" * 40)
    print("OpenPDF Encoder 2026")
    print("By Fjord Enzo Bertrand-Helmgens")
    print("=" * 40)

def main():
    parser = argparse.ArgumentParser(description="OpenPDF compiler")
    parser.add_argument("--text")
    parser.add_argument("--out", required=True)
    parser.add_argument("--title")
    parser.add_argument("--author")
    parser.add_argument("--password")
    parser.add_argument("--diag", action="store_true")
    parser.add_argument("--silent", action="store_true")

    args = parser.parse_args()

    if not args.silent:
        display_header()

    if args.diag:
        print(f"[DIAG] OS: {platform.system()} {platform.release()}")
        print(f"[DIAG] CPU: {platform.machine()}")
        print(f"[DIAG] Runtime: Python {sys.version.split()[0]}")

    engine = OpenPDFEngine(
        author=args.author, 
        title=args.title, 
        password=args.password
    )

    try:
        engine.process_file(args.text, args.out)
        if not args.silent:
            print(f"[SUCCESS] File saved: {args.out}")
    except Exception as e:
        print(f"[FATAL] System error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if hasattr(sys.stdin, 'isatty') and sys.stdin.isatty():
        pass 
    main()