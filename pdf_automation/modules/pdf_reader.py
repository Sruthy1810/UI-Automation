import pdfplumber


def read_pdf(pdf_path):

    extracted_text = ""

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            text = page.extract_text()

            if text:
                extracted_text += text + "\n"

    return extracted_text