from openpyxl import load_workbook
from config.config_reader import get_product_file
from utils.logger import logger
from openpyxl.styles import PatternFill
import math
import re

GREEN = PatternFill("solid", fgColor="C6EFCE")
RED = PatternFill("solid", fgColor="FFC7CE")

def is_missing(value):
    """True if a cell is empty. 0 is treated as a real value."""
    return value is None or str(value).strip() == ""


def mark_rows_red(row_numbers):
    """
    Color the given Excel rows red and clear their 'Found/Not' cell.
    Never raises, so it can't stop the bot.
    """

    if not row_numbers:
        return

    workbook = None

    try:
        file_path = get_product_file()

        workbook = load_workbook(filename=str(file_path))
        sheet = workbook.active

        red_fill = PatternFill(fill_type="solid", fgColor="FF0000")

        headers = {}

        for cell in sheet[1]:
            if cell.value:
                headers[str(cell.value).strip()] = cell.column

        status_col = headers.get("Status")

        for row in row_numbers:

            for column in range(1, sheet.max_column + 1):
                sheet.cell(row=row, column=column).fill = red_fill

            # No result for an unprocessed row
            if status_col:
               sheet.cell(row=row, column=status_col).value = None

        workbook.save(str(file_path))

        logger.info(f"Marked rows red (missing data): {row_numbers}")

    except PermissionError:
        logger.error(
            "Could not mark rows: the file is open. Close it and run again."
        )

    except Exception as e:
        logger.error(f"Could not mark rows red: {e}")

    finally:
        if workbook:
            workbook.close()


SIZE_MAP = {
    "EXTRA SMALL": "XS", "X-SMALL": "XS", "XSMALL": "XS",
    "SMALL": "S",
    "MEDIUM": "M",
    "LARGE": "L",
    "EXTRA LARGE": "XL", "X-LARGE": "XL", "XLARGE": "XL",
    "2XL": "XXL", "XXL": "XXL",
    "3XL": "XXXL", "XXXL": "XXXL",
    "FREE SIZE": "Free Size", "FREESIZE": "Free Size",
    "FREE": "Free Size", "FS": "Free Size", "F/S": "Free Size",
    "ONE SIZE": "Free Size", "OS": "Free Size",
}

BLANKS = {"", "nan", "none", "na", "n/a", "-", "--"}

def normalize_size(value):
    """40, 40.0, ' s ', '3xl' -> '40', '40', 'S', '3XL'. Returns None if empty."""
    if value is None:
        return None
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    size = str(value).strip().upper()
    if size in ("", "NAN", "NONE", "N/A", "-"):
        return None
    return size



def read_products():

    file_path = get_product_file()

    print(f"Reading product Excel: {file_path}")

    workbook = load_workbook(
        filename=str(file_path),
        data_only=True
    )

    sheet = workbook.active

    products = []
    invalid_rows = []

    headers = [str(c.value).strip() if c.value else "" for c in sheet[1]]

    # --------------------------------
    # Validate required columns
    # --------------------------------
    required_columns = [
        "Name", "Product", "Price", "Customer Ratings",
         "Email", "Status", "Remarks", "Size"
    ]

    for column in required_columns:
        if column not in headers:
            raise ValueError(f"{column} column not found in Excel.")

    mandatory_columns = ["Name", "Product", "Price", "Customer Ratings", "Email"]

    # --------------------------------
    # Read customer rows
    # --------------------------------
    for row_num, row in enumerate(
        sheet.iter_rows(min_row=2, values_only=True), start=2
    ):
        data = dict(zip(headers, row))   # includes Status and Remarks

        missing = [c for c in mandatory_columns if is_missing(data.get(c))]

        # Completely empty row: ignore
        if len(missing) == len(mandatory_columns):
            continue

        # Some data missing: skip row and mark it red
        if missing:
            invalid_rows.append(row_num)
            logger.warning(
                f"Row {row_num} skipped, missing: {', '.join(missing)}"
            )
            continue

        products.append({
            "Row": row_num,
            "Name": str(data["Name"]).strip(),
            "Product": str(data["Product"]).strip(),
            "Price": data["Price"],
            "Customer Ratings": data["Customer Ratings"],
            "Email": str(data["Email"]).strip(),
            "Size": normalize_size(data.get("Size")),
            "Status": data.get("Status"),
            "Remarks": data.get("Remarks"),
        })

    workbook.close()

    # Color invalid rows (after the workbook is closed)
    mark_rows_red(invalid_rows)

    print(f"Products found: {len(products)}")
    logger.info(f"Products found: {len(products)}")

    if invalid_rows:
        logger.info(f"Rows skipped due to missing data: {len(invalid_rows)}")

    return products

def update_found_status(product, status, name=None, row_num=None):
    """
    Write 'Found' / 'Not Found' in the 'Found/Not' column (that cell only).
    Uses row_num when given, otherwise matches Product (and Name).
    Never raises, so it can't stop the bot.
    """
    workbook = None
    try:
        file_path = get_product_file()
        workbook = load_workbook(filename=str(file_path))
        sheet = workbook.active

        headers = {str(c.value).strip(): c.column for c in sheet[1] if c.value}
        product_col = headers.get("Product")
        name_col = headers.get("Name")
        status_col = headers.get("Status")
        remarks_col = headers.get("Remarks")

        if not status_col:
            logger.error("Excel column 'Status' not found.")
            return

        target_row = row_num

        if target_row is None and product_col:
            for row in range(2, sheet.max_row + 1):
                if str(sheet.cell(row=row, column=product_col).value or "").strip().lower() \
                        != str(product).strip().lower():
                    continue
                if name and name_col and \
                        str(sheet.cell(row=row, column=name_col).value or "").strip().lower() \
                        != str(name).strip().lower():
                    continue
                target_row = row
                break

        if target_row is None:
            logger.error(f"Row not found in Excel for product: {product}")
            return

        cell = sheet.cell(row=target_row, column=status_col)
        cell.value = status
        cell.fill = GREEN if status.strip().lower() == "found" else RED

        workbook.save(str(file_path))
        logger.info(f"Excel row {target_row}: Found/Not={status}")

    except PermissionError:
        logger.error("Could not update Excel: the file is open. Close it and run again.")
    except Exception as e:
        logger.error(f"Could not update Excel: {e}")
    finally:
        if workbook:
            workbook.close()

def update_cart_status(product,  status, remarks, name=None, row_num=None,excel_path=None,):
    """Write Status (Success/Failed) and Remarks for one Excel row.
    Uses row_num when given, otherwise matches Product (and Name)."""
    try:
        excel_path = excel_path or get_product_file()
        wb = load_workbook(excel_path)
        ws = wb.active

        headers = {
            str(c.value).strip(): c.column
            for c in ws[1] if c.value is not None
        }

        # Create the columns if missing
        for col_name in ("Status", "Remarks"):
            if col_name not in headers:
                new_col = ws.max_column + 1
                ws.cell(row=1, column=new_col, value=col_name)
                headers[col_name] = new_col

        target_row = row_num

        # Fallback: find the row by Product (and Name)
        if target_row is None:
            product_col = headers["Product"]
            name_col = headers.get("Name")

            for row in range(2, ws.max_row + 1):
                if str(ws.cell(row, product_col).value).strip() != str(product).strip():
                    continue
                if name and name_col and \
                        str(ws.cell(row, name_col).value).strip() != str(name).strip():
                    continue
                target_row = row
                break

        if target_row is None:
            logger.warning(f"Excel row not found for product: {product}")
            wb.close()
            return

        status_cell = ws.cell(row=target_row, column=headers["Status"])
        status_cell.value = status
        status_cell.fill = GREEN if status == "Success" else RED

        ws.cell(row=target_row, column=headers["Remarks"]).value = str(remarks)[:250]

        wb.save(excel_path)
        wb.close()
        logger.info(f"Excel row {target_row}: Status={status}")

    except PermissionError:
        logger.error("Could not save Excel. Close product.xlsx and run again.")
    except Exception as e:
        logger.error(f"Excel update failed for '{product}': {e}")


def is_already_found(product_data):
    status = str(product_data.get("Status") or "").strip().lower()
    return status == "found"