
import pdfplumber
import sys
import os

pdf_path = os.path.join("Material", "chandassu wesite info material.pdf")
output_path = "pdf_content.txt"

try:
    with pdfplumber.open(pdf_path) as pdf:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"Total Pages: {len(pdf.pages)}\n")
            for i, page in enumerate(pdf.pages):
                f.write(f"--- Page {i+1} ---\n")
                text = page.extract_text()
                f.write(text if text else "[No Text Extracted]")
                f.write("\n\n")
                
                if page.images:
                    f.write(f"Found {len(page.images)} images on page {i+1}\n")

    print("Done")
except Exception as e:
    print(f"Error reading PDF: {e}")
