import pytesseract
import cv2
import numpy as np

pytesseract.pytesseract.tesseract_cmd = (
    r"C:/Program Files/Tesseract-OCR/tesseract.exe"
)


def extract_text_from_pages(pages):
    all_text = []

    for page in pages:
        image = cv2.cvtColor(
            np.array(page),
            cv2.COLOR_RGB2BGR
        )

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        text = pytesseract.image_to_string(
            gray,
            config="--psm 6"
        )

        all_text.append(text)

    return "\n".join(all_text)