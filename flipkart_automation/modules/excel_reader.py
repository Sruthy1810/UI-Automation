from openpyxl import load_workbook
from config.config_reader import get_product_file
from utils.logger import logger
from openpyxl.styles import PatternFill

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
    logger.info(f"Products found: {len(products)}")

    return products

def update_found_status(product, status, name=None):
    """
    Write 'Found' / 'Not Found' in the 'Found/Not' column.
    If 'Not Found', the whole row is colored red.
    If 'Found', any old color on that row is cleared.
    Never raises, so it can't stop the bot.
    """

    workbook = None

    try:
        file_path = get_product_file()

        workbook = load_workbook(filename=str(file_path))
        sheet = workbook.active

        red_fill = PatternFill(fill_type="solid", fgColor="FF0000")
        no_fill = PatternFill(fill_type=None)

        headers = {}

        for cell in sheet[1]:
            if cell.value:
                headers[str(cell.value).strip()] = cell.column

        product_col = headers.get("Product")
        name_col = headers.get("Name")
        status_col = headers.get("Found/Not")

        if not product_col or not status_col:
            logger.error("Excel columns 'Product' or 'Found/Not' not found.")
            return

        updated = False

        for row in range(2, sheet.max_row + 1):

            cell_product = str(
                sheet.cell(row=row, column=product_col).value or ""
            ).strip()

            if cell_product.lower() != str(product).strip().lower():
                continue

            # If Name is available, make sure it matches too
            if name and name_col:
                cell_name = str(
                    sheet.cell(row=row, column=name_col).value or ""
                ).strip()

                if cell_name.lower() != str(name).strip().lower():
                    continue

            # Write the status
            sheet.cell(row=row, column=status_col).value = status

            # Red for Not Found, no color for Found
            fill = red_fill if status.strip().lower() == "not found" else no_fill

            for column in range(1, sheet.max_column + 1):
                sheet.cell(row=row, column=column).fill = fill

            updated = True
            break

        if updated:
            workbook.save(str(file_path))
            logger.info(f"Excel updated: {product} -> {status}")
        else:
            logger.error(f"Row not found in Excel for product: {product}")

    except PermissionError:
        logger.error(
            "Could not update Excel: the file is open. Close it and run again."
        )

    except Exception as e:
        logger.error(f"Could not update Excel: {e}")

    finally:
        if workbook:
            workbook.close()