import pdfplumber

try:
    with pdfplumber.open('TP0XAI.pdf') as pdf:
        print(f"Total pages: {len(pdf.pages)}\n")
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            print(f"\n{'='*60}")
            print(f"PAGE {i+1}")
            print(f"{'='*60}\n")
            print(text)
            if i >= 2:  # First 3 pages
                break
except Exception as e:
    print(f"Error: {e}")
