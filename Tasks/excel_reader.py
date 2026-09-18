from openpyxl import load_workbook


def read_employee_data(file_path):

    workbook = load_workbook(file_path)

    sheet = workbook.active

    employees = []

    headers = [
        cell.value
        for cell in sheet[1]
    ]


    for row in sheet.iter_rows(
        min_row=2,
        values_only=True
    ):

        employee = dict(
            zip(headers, row)
        )

        employees.append(employee)

    return employees