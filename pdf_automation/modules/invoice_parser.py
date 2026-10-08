import re


def extract_invoice_details(text):

    details = {
        "invoice_number": "",
        "invoice_date": "",
        "total_amount": "",
        "tax": "",
        "from_person": "",
        "to_person": ""
    }

    # --------------------------------
    # Invoice Number
    # --------------------------------
    match = re.search(
        r"Invoice Number\s+([A-Za-z0-9-]+)",
        text,
        re.IGNORECASE
    )

    if match:
        details["invoice_number"] = match.group(1).strip()

    # --------------------------------
    # Invoice Date
    # --------------------------------
    match = re.search(
        r"Invoice Date\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})",
        text,
        re.IGNORECASE
    )

    if match:
        details["invoice_date"] = match.group(1).strip()


    # --------------------------------
    # Sub Total
    # --------------------------------

    match =re.search(
        r"Sub Total\s+\$([\d,]+\.\d{2})",
        text,
        re.IGNORECASE
    )
    if match:
        details["subtotal"] = "$" + match.group(1)


    # --------------------------------
    # Tax
    # --------------------------------

    match = re.search(
        r"Tax\s+\$([\d,]+\.\d{2})",
        text,
        re.IGNORECASE
    )

    if match:
        details["tax"] = "$" + match.group(1)

    # --------------------------------
    # Total Amount
    # --------------------------------

    match = re.search(
        r"(?m)^Total\s+\$([\d,]+\.\d{2})",
        text,
        re.IGNORECASE
    )

    if match:
        details["total_amount"] = "$" + match.group(1)


    # --------------------------------
    # From
    # --------------------------------

    from_match = re.search(
        r"From:\s*(.*?)(?=\s*To:)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if from_match:
        from_text = from_match.group(1).strip()

        # Remove unwanted invoice fields
        from_text = re.sub(
            r"\s*(Order Number\s+\S+|Invoice Date\s+[A-Za-z]+\s+\d{1,2},\s+\d{4}|Due Date\s+[A-Za-z]+\s+\d{1,2},\s+\d{4}|Total Due\s+\$[\d,]+\.\d{2})",
            "",
            from_text,
            flags=re.IGNORECASE
        )

        details["from_person"] = from_text.strip()

    # --------------------------------
    # To
    # --------------------------------
    to_match = re.search(
        r"To:\s*(.*?)\s*Hrs/Qty",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if to_match:
        details["to_person"] = to_match.group(1).strip()

    return details