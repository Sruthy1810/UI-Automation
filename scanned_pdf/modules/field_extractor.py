
import re


def extract_title(text):
    # Match known court names and return their exact standardized titles.
    # OCR may contain extra characters before or after the court name.
    if re.search(r"\bDENVER\s+COUNTY\s+COURT\b", text, re.IGNORECASE):
        return "DENVER COUNTY COURT"

    if re.search(
        r"\bCOUNTY\s+COURT\s*,?\s*WELD\s+COUNTY\b",
        text,
        re.IGNORECASE
    ):
        return "County Court, Weld County"

    return None


def extract_fields(text):
    results = []
    text = text.replace("\x0c", "\n")

    # 1. Extract the exact court title
    title = extract_title(text)

    # 2. Split page into individual records
    record_pattern = (
        r"(?=^[ \t]*Time\s*:\s*\d{1,2}:\d{2}\s*[AP]M\b|"
        r"^[ \t]*20\d{2}\s*C\s*-\s*\d{5,}\b)"
    )

    records = re.split(
        record_pattern,
        text,
        flags=re.IGNORECASE | re.MULTILINE
    )

    for record in records:

        is_denver = bool(re.search(
            r"\bCase\s*No\.?\s*:\s*\d{2}\s*C?\s*\d+",
            record,
            re.IGNORECASE
        ))

        is_weld = bool(re.search(
            r"\b20\d{2}\s*C\s*-\s*\d{5,}\b",
            record,
            re.IGNORECASE
        ))

        if not (is_denver or is_weld):
            continue

        account_number = None
        principal = None

        # 3. Extract account number
        if is_denver:
            # Example: Court Type: Return Date 20520021
            account_match = re.search(
                r"Court\s*Type\s*:\s*Return\s*Date"
                r"\s*:?\s*(?:\s*\n\s*)?(\d{6,})\b",
                record,
                re.IGNORECASE
            )

            if account_match:
                account_number = account_match.group(1)

        elif is_weld:
            # Find the defendant/account-number section after "vs."
            vs_match = re.search(
                r"\bvs\.?\s*(.*?)"
                r"(?=Return\s+of\s+Service|$)",
                record,
                re.IGNORECASE | re.DOTALL
            )

            if vs_match:
                for line in vs_match.group(1).splitlines():
                    line = line.strip()

                    # Match an account number, allowing spaces between digits.
                    number_match = re.match(
                        r"^\s*((?:\d[\d ]{4,}\d))\s+(?=[A-Z])",
                        line,
                        re.IGNORECASE
                    )

                    if number_match:
                        digits = re.sub(
                            r"\D", "", number_match.group(1)
                        )

                        if len(digits) >= 6:
                            account_number = digits
                            break

        # 4. Extract principal from its own line
        for line in record.splitlines():
            principal_label = re.search(
                r"\bPrincipal\s*:\s*(.*)",
                line,
                re.IGNORECASE
            )

            if not principal_label:
                continue

            amount_text = principal_label.group(1)

            # Accept amounts such as 1418.97 or 2,158.76.
            # Reject malformed OCR values such as 1.881.95.
            amount_match = re.search(
                r"(?<![\d.,])(\d[\d,]*\.\d{2})(?![\d.,])",
                amount_text
            )

            if amount_match:
                principal = amount_match.group(1).replace(",", "")

            break

        # 5. Mark incomplete or uncertain records
        review_required = (
            "Yes"
            if title is None
            or account_number is None
            or principal is None
            else "No"
        )

        results.append({
            "Title": title or "Not found",
            "Account Number": account_number or "Not found",
            "Principal": principal or "Not found",
            "Review Required": review_required
        })

    return results