import re
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from config.config_reader import get_product_file
from utils.logger import logger
import time
GREEN = PatternFill("solid", fgColor="C6EFCE")
RED = PatternFill("solid", fgColor="FFC7CE")


def is_missing(value):
    """True if a cell is empty. 0 is treated as a real value."""
    return value is None or str(value).strip() == ""


# ---------------- SIZE HANDLING ----------------

BLANKS = {"", "nan", "none", "na", "n/a", "-", "--"}

# words in Excel -> letters on Flipkart
SIZE_WORDS = {
    "EXTRA SMALL": "XS", "X-SMALL": "XS", "XSMALL": "XS",
    "SMALL": "S", "MEDIUM": "M", "LARGE": "L",
    "EXTRA LARGE": "XL", "X-LARGE": "XL", "XLARGE": "XL",
    "FREESIZE": "FREE SIZE", "FREE": "FREE SIZE", "FS": "FREE SIZE",
    "F/S": "FREE SIZE", "ONE SIZE": "FREE SIZE", "OS": "FREE SIZE",
}

# other spellings Flipkart may use for the same size
SIZE_ALIASES = {"3XL": "XXXL", "XXXL": "3XL", "2XL": "XXL", "XXL": "2XL",
                "4XL": "XXXXL", "XXXXL": "4XL"}


def normalize_size(value):
    """Clean the Excel cell but keep combos: 40.0 -> '40', ' s ' -> 'S', '40/s' -> '40/S'."""
    if value is None:
        return None
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    size = str(value).strip().upper()
    if size.lower() in BLANKS:
        return None
    return size


def parse_sizes(value):
    """'40/S' -> ['40','S'];  'S,3XL' -> ['S','3XL','XXXL']"""
    if value is None:
        return []
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    result = []
    for part in re.split(r"[/,;|]+", text):
        part = part.strip().upper()
        part = SIZE_WORDS.get(part, part)
        if part and part.lower() not in BLANKS and part not in result:
            result.append(part)
            alias = SIZE_ALIASES.get(part)
            if alias and alias not in result:
                result.append(alias)
    return result


# ---------------- EXCEL WRITING ----------------

def mark_rows_red(row_numbers):
    """
    Color the given Excel rows red and clear their Status/Remarks cells.
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
        headers = {str(c.value).strip(): c.column for c in sheet[1] if c.value}
        status_col = headers.get("Status")
        remarks_col = headers.get("Remarks")

        for row in row_numbers:
            for column in range(1, sheet.max_column + 1):
                sheet.cell(row=row, column=column).fill = red_fill
            if status_col:
                sheet.cell(row=row, column=status_col).value = None
            if remarks_col:
                sheet.cell(row=row, column=remarks_col).value = "Skipped: mandatory data missing"

        workbook.save(str(file_path))
        logger.info(f"Marked rows red (missing data): {row_numbers}")

    except PermissionError:
        logger.error("Could not mark rows: the file is open. Close it and run again.")
    except Exception as e:
        logger.error(f"Could not mark rows red: {e}")
    finally:
        if workbook:
            workbook.close()


def update_status(product, status, remarks="", name=None, row_num=None,
                  excel_path=None, retries=3):
    """
    Write Status ('Success' / 'Failed') + Remarks and colour the WHOLE row
    (green = Success, red = Failed). Retries if the file is locked.
    Returns True if saved.
    """
    for attempt in range(1, retries + 1):
        workbook = None
        try:
            path = excel_path or get_product_file()
            workbook = load_workbook(str(path))
            sheet = workbook.active

            headers = {str(c.value).strip(): c.column for c in sheet[1] if c.value}

            for col_name in ("Status", "Remarks"):
                if col_name not in headers:
                    new_col = sheet.max_column + 1
                    sheet.cell(row=1, column=new_col, value=col_name)
                    headers[col_name] = new_col

            target_row = row_num

            if target_row is None:
                product_col = headers.get("Product")
                name_col = headers.get("Name")
                if product_col:
                    for r in range(2, sheet.max_row + 1):
                        if str(sheet.cell(r, product_col).value or "").strip().lower() \
                                != str(product).strip().lower():
                            continue
                        if name and name_col and \
                                str(sheet.cell(r, name_col).value or "").strip().lower() \
                                != str(name).strip().lower():
                            continue
                        target_row = r
                        break

            if target_row is None:
                logger.error(f"Excel row not found for product: {product}")
                return False

            sheet.cell(row=target_row, column=headers["Status"]).value = status
            sheet.cell(row=target_row, column=headers["Remarks"]).value = str(remarks)[:250]

            fill = GREEN if str(status).strip().lower() == "success" else RED
            for col in range(1, sheet.max_column + 1):
                sheet.cell(row=target_row, column=col).fill = fill

            workbook.save(str(path))
            logger.info(f"Excel row {target_row}: Status={status} | Remarks={remarks}")
            return True

        except PermissionError:
            logger.warning(f"Excel is open/locked (attempt {attempt}/{retries}). Retrying...")
            time.sleep(2)
        except Exception as e:
            logger.error(f"Excel update failed for '{product}': {e}")
            return False
        finally:
            if workbook:
                workbook.close()

    logger.error(f"COULD NOT SAVE Excel for '{product}'. Close product.xlsx and pause OneDrive sync.")
    return False


update_cart_status = update_status


def update_found_status(*args, **kwargs):
    """No-op: the Found/Not column was removed. Kept so old imports don't break."""
    return None

def sync_row_colors(retries=3):
    """
    Repaint every data row from its Status cell:
      Success -> green, Failed -> light red. Other rows are left alone.
    Fixes old colours left by earlier versions. Never raises.
    """
    for attempt in range(1, retries + 1):
        workbook = None
        try:
            path = get_product_file()
            workbook = load_workbook(str(path))
            sheet = workbook.active

            headers = {str(c.value).strip(): c.column for c in sheet[1] if c.value}
            status_col = headers.get("Status")
            if not status_col:
                return

            changed = 0
            for row in range(2, sheet.max_row + 1):
                status = str(sheet.cell(row, status_col).value or "").strip().lower()
                if status == "success":
                    fill = GREEN
                elif status == "failed":
                    fill = RED
                else:
                    continue
                for col in range(1, sheet.max_column + 1):
                    sheet.cell(row=row, column=col).fill = fill
                changed += 1

            if changed:
                workbook.save(str(path))
                logger.info(f"Row colours synced for {changed} row(s)")
            return

        except PermissionError:
            logger.warning(f"Excel is open/locked (attempt {attempt}/{retries}). Retrying...")
            time.sleep(2)
        except Exception as e:
            logger.error(f"Could not sync row colours: {e}")
            return
        finally:
            if workbook:
                workbook.close()


def is_already_success(product_data):
    """True if this row was already processed successfully (skip it on rerun)."""
    return str(product_data.get("Status") or "").strip().lower() == "success"


is_already_found = is_already_success


# ---------------- EXCEL READING ----------------

def read_products():

    file_path = get_product_file()
    print(f"Reading product Excel: {file_path}")

    workbook = load_workbook(filename=str(file_path), data_only=True)
    sheet = workbook.active

    products = []
    invalid_rows = []

    headers = [str(c.value).strip() if c.value else "" for c in sheet[1]]

    # Validate required columns
    required_columns = [
        "Name", "Product", "Price", "Customer Ratings",
        "Email", "Status", "Remarks", "Size"
    ]
    for column in required_columns:
        if column not in headers:
            raise ValueError(f"{column} column not found in Excel.")

    mandatory_columns = ["Name", "Product", "Price", "Customer Ratings", "Email"]

    # Read customer rows
    for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        data = dict(zip(headers, row))

        missing = [c for c in mandatory_columns if is_missing(data.get(c))]

        # Completely empty row: ignore
        if len(missing) == len(mandatory_columns):
            continue

        # Some data missing: skip row and mark it red
        if missing:
            invalid_rows.append(row_num)
            logger.warning(f"Row {row_num} skipped, missing: {', '.join(missing)}")
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
    sync_row_colors()

    print(f"Products found: {len(products)}")
    logger.info(f"Products found: {len(products)}")

    if invalid_rows:
        logger.info(f"Rows skipped due to missing data: {len(invalid_rows)}")

    return products