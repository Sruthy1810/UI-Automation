from openpyxl import load_workbook
from config.config_reader import get_product_file


def read_products():

    file_path = get_product_file()

    print(f"Reading product Excel: {file_path}")

    workbook = load_workbook(
        filename=str(file_path),
        data_only=True
    )

    sheet = workbook.active

    products = []

    # Find Product column
    headers = {}

    for cell in sheet[1]:

        if cell.value:

            headers[
                str(cell.value).strip()
            ] = cell.column


    # --------------------------------
    # Validate required columns
    # --------------------------------

    required_columns = [
        "Name",
        "Product",
        "Price",
        "Customer Ratings",
        "Found/Not",
        "Email"
    ]

    for column in required_columns:

        if column not in headers:

            raise ValueError(
                f"{column} column not found in Excel."
            )

    # --------------------------------
    # Read customer rows
    # --------------------------------

    for row in range(2, sheet.max_row + 1):

        name = sheet.cell(
            row=row,
            column=headers["Name"]
        ).value

        product = sheet.cell(
            row=row,
            column=headers["Product"]
        ).value

        price = sheet.cell(
            row=row,
            column=headers["Price"]
        ).value

        rating = sheet.cell(
            row=row,
            column=headers["Customer Ratings"]
        ).value

        email = sheet.cell(
            row=row,
            column=headers["Email"]
        ).value

        # Skip empty rows
        if not name or not product:
            continue

        customer = {
            "Name": str(name).strip(),
            "Product": str(product).strip(),
            "Price": price,
            "Customer Ratings": rating,
            "Email": str(email).strip() if email else ""
        }

        products.append(customer)

    workbook.close()

    print(f"Products found: {len(products)}")

    return products