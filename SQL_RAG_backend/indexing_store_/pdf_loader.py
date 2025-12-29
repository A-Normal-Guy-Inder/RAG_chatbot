import os
import fitz
from PIL import Image
import pytesseract
from io import BytesIO
from langchain_core.documents import Document
from langchain_community.document_loaders import UnstructuredPDFLoader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "..", "..", "Pdfs")

print("PDF directory:", PDF_DIR)


def load_pdfs():
    all_docs = []

    for filename in os.listdir(PDF_DIR):
        if not filename.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(PDF_DIR, filename)
        print(f"\nProcessing: {pdf_path}")

        # --- Load normal extracted text ---
        loader = UnstructuredPDFLoader(
            pdf_path,
            strategy="hi_res",
            extract_images_in_pdf=True
        )

        text_docs = loader.load()

        # --- Open PDF to read embedded images ---
        pdf = fitz.open(pdf_path)
        image_docs = []

        for page_index, page in enumerate(pdf):
            for _, img in enumerate(page.get_images()):
                xref = img[0]
                pix = fitz.Pixmap(pdf, xref)

                # Convert to RGB if needed
                if pix.n > 3:
                    pix = fitz.Pixmap(fitz.csRGB, pix)

                # Convert pixmap to bytes (NO FILE SAVED)
                img_bytes = pix.tobytes("png")
                image_stream = BytesIO(img_bytes)

                # Open image directly from memory
                pil_img = Image.open(image_stream)

                # OCR
                ocr_text = pytesseract.image_to_string(pil_img)

                if not ocr_text.strip():
                    continue

                image_docs.append(
                    Document(
                        page_content=ocr_text.strip(),
                        metadata={
                            "source": filename,
                            "page": page_index + 1,
                            "type": "image_ocr"
                        }
                    )
                )

        print(f"  -> OCR text docs: {len(text_docs)}")
        print(f"  -> OCR image docs: {len(image_docs)}")

        all_docs.extend(text_docs + image_docs)

    print(f"\nTotal combined docs: {len(all_docs)}")
    return all_docs