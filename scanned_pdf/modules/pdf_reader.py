from pdf2image import convert_from_path
import pytesseract


def read_scanned_pdf(pdf_path):
    poppler_path = r"C:/Users/Admin/Downloads/Release-26.09.0-0/poppler-26.09.0/Library/bin"

    pages = convert_from_path(
        pdf_path,
        dpi=300,
        poppler_path=poppler_path
    )

    # Continue with your OCR logic here
    return pages