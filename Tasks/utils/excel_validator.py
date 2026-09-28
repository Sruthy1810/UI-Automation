MANDATORY_COLUMNS = [
    "First Name",
    "Last Name",
    "Employee Id",
    "Nationality",
    "Marital Status",
    "Gender",
    "Date of Birth",
    "Blood Group",
    "Document"
]


def validate_employee_data(employees):

    errors = []

    for row_number, employee in enumerate(employees, start=2):

        missing_fields = []

        for column in MANDATORY_COLUMNS:

            value = employee.get(column)

            if value is None or str(value).strip() == "":
                missing_fields.append(column)

        if missing_fields:

            employee_name = (
                f"{employee.get('First Name', '')} "
                f"{employee.get('Last Name', '')}"
            ).strip()

            errors.append({
                "row": row_number,
                "employee": employee_name,
                "missing": missing_fields
            })

    return errors