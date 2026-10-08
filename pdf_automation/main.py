from config.config_reader import pdf_file
from modules.pdf_reader import read_pdf
from modules.invoice_parser import extract_invoice_details


pdf_path = pdf_file()

print("PDF Path:", pdf_path)
text = read_pdf(pdf_file())
# Clean unwanted single-character lines
lines = text.splitlines()

clean_lines = []

for line in lines:
    line = line.strip()

    if len(line) == 1 and line.isalpha():
        continue

    clean_lines.append(line)

# Convert cleaned lines back to text
clean_text = "\n".join(clean_lines)

details = extract_invoice_details(clean_text)

print(details)


print("\n========== INVOICE DETAILS ==========")

print("Invoice Number :", details["invoice_number"])
print("Invoice Date   :", details["invoice_date"])
print("Subtotal       :", details["subtotal"])
print("Tax            :", details["tax"])
print("Total Amount   :", details["total_amount"])


print("\nFrom:")
print(details["from_person"])

print("\nTo:")
print(details["to_person"])

print("=====================================")