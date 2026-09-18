import os
from pathlib import Path
from logger import logger

def create_employee(page, employee):

    try:
        # =====================================================
        # 1. GET EMPLOYEE DATA
        # =====================================================

        first_name = str(employee["First Name"]).strip()
        last_name = str(employee["Last Name"]).strip()

        print("\n----------------------------------------")
        print(f"Creating employee: {first_name} {last_name}")
        print("----------------------------------------")

        # =====================================================
        # 2. ENTER FIRST NAME
        # =====================================================

        page.get_by_placeholder("First Name").fill(first_name)

        # =====================================================
        # 3. ENTER MIDDLE NAME IF EXISTS
        # =====================================================

        middle_name = employee.get("Middle Name")

        if middle_name and str(middle_name).strip():

            page.get_by_placeholder("Middle Name").fill(
                str(middle_name).strip()
            )

            print(f"Middle Name: {middle_name}")

        else:
            print("Middle Name: Not provided")

        # =====================================================
        # 4. ENTER LAST NAME
        # =====================================================

        page.get_by_placeholder("Last Name").fill(last_name)

         # =====================================================
         # 4.1 ENTER EMPLOYEE ID
         # =====================================================


        employee_id = page.locator(
                     "label.oxd-label",
                     has_text="Employee Id"
                 ).locator("xpath=following::input[1]")
             
        employee_id.fill("")
        employee_id.fill(str(employee["Employee Id"]))



        # =====================================================
        # 5. FIND PROFILE PHOTO
        # =====================================================

        base_dir = Path(__file__).resolve().parent
        assets_dir = base_dir / "assets"

        photo_path = assets_dir / f"{first_name} {last_name}.jpg"

        print("\nPhoto path:")
        print(photo_path)

        # =====================================================
        # 6. CHECK PHOTO
        # =====================================================

        if not photo_path.is_file():

            print("PHOTO NOT FOUND")
            print(f"Expected file: {photo_path}")

            print("\nFiles available inside assets:")

            if assets_dir.exists():

                for file in assets_dir.iterdir():
                    print(" -", file.name)

            else:
                print("assets folder does not exist")

            return False

        print("Photo found")
        print(f"File: {photo_path.name}")

        # =====================================================
        # 7. UPLOAD PROFILE IMAGE
        # =====================================================

        print("\nUploading profile image...")

        try:

            with page.expect_file_chooser(timeout=10000) as file_chooser_info:

                page.locator(
                    "button.employee-image-action"
                ).click()

            file_chooser = file_chooser_info.value

            file_chooser.set_files(
                str(photo_path.resolve())
            )

            print("Profile picture uploaded")

        except Exception as upload_error:

            print("\nPROFILE IMAGE UPLOAD FAILED")
            print(upload_error)

            return False

        # =====================================================
        # 8. WAIT FOR IMAGE
        # =====================================================

        page.wait_for_timeout(1500)

        # =====================================================
        # 9. SAVE EMPLOYEE
        # =====================================================

        print("\nSaving employee...")

        page.get_by_role(
            "button",
            name="Save"
        ).click()

        # =====================================================
        # 10. WAIT FOR PERSONAL DETAILS PAGE
        # =====================================================

        print("Waiting for Personal Details page...")

        page.wait_for_url("**/pim/viewPersonalDetails/empNumber/**", timeout=30000)

        print("Moved to Personal Details page")
        print("Current URL:", page.url)

        # =====================================================
        # 11. WAIT FOR PERSONAL DETAILS TO APPEAR
        # =====================================================

        page.get_by_role("link", name="Personal Details", exact=True).wait_for(
         state="visible",timeout=10000)
            


        print(
            f"Entered: {first_name} {last_name}"
            f" | Employee ID: {employee['Employee Id']}"
        )

        print("Personal Details page opened")

        # =====================================================
        # 12. NATIONALITY
        # =====================================================

        fill_dropdown(page, "Nationality", employee["Nationality"])

        # =====================================================
        # 13. MARITAL STATUS
        # =====================================================

        
        fill_dropdown(page, "Marital Status", employee["Marital Status"])
        

        # =====================================================
        # 14. GENDER
        # =====================================================

        select_gender(page, employee["Gender"])

        # =====================================================
        # 15. DATE OF BIRTH
        # =====================================================

        enter_date_of_birth(
        page,
        employee["Date of Birth"]
    )

        print("Personal Details filled successfully")

        # =====================================================
        #   SAVE PERSONAL DETAILS
         # =====================================================
        #page.get_by_role(
           #         "button",
          #          name="Save"
         #       ).click()
        
        #page.wait_for_timeout(1000)
        
        

        personal_details_form = page.locator(
        "form.oxd-form"
        ).filter(has=page.locator("label", has_text="Employee Full Name"))

        personal_details_form.get_by_role("button", name="Save").click()

        print("Employee Personal details updated")

        # =====================================================
        # 16. BLOOD GROUP
        # =====================================================

        fill_dropdown(
            page,
            "Blood Type",
            employee["Blood Group"]
        )

        logger.info("Employee Personal details filled successfully")

        # =====================================================
        # 17. SAVE PERSONAL DETAILS
        # =====================================================

        custom_fields_form = page.locator(
        "form.oxd-form"
        ).filter(has=page.locator("label", has_text="Blood Type"))

        custom_fields_form.get_by_role("button", name="Save").click()

        print("Employee details updated")


        # =====================================================
        #  UPLOAD DOCUMENT
        # =====================================================

        
        upload_document(
            page,
            employee
        )

        # 19. SUCCESS
        logger.info(
            f"Employee created successfully: "
            f"{first_name} {last_name}"
        )

        return True

    except Exception as e:

        print("\nEMPLOYEE CREATION FAILED")
        print(e)

        return False


# ==========================================================
# DROPDOWN HELPER
# ==========================================================

def fill_dropdown(page, label, value):
    print(f"Selecting {label}: {value}")

    # Find the input group containing the required label
    group = page.locator(
        ".oxd-input-group"
    ).filter(
        has=page.locator("label", has_text=label)
    )

    # Click the custom dropdown
    group.locator(".oxd-select-text").click()

    # Select the required option
    page.locator(
        ".oxd-select-option"
    ).filter(
        has_text=str(value).strip()
    ).click()

    print(f"{label} selected successfully")

# ==========================================================
# Gender Helper
# ==========================================================


def select_gender(page, gender):

    gender = str(gender).strip()

    print(f"Selecting Gender: {gender}")

    page.get_by_role(
        "radio",
        name=gender,
        exact=True
    ).check(force=True)

    print("Gender selected successfully")

# ==========================================================
# DATE OF BIRTH HELPER
# ==========================================================

def enter_date_of_birth(page, dob):

    print(f"Entering Date of Birth: {dob}")

    if hasattr(dob, "strftime"):
        dob_value = dob.strftime("%Y-%m-%d")
    else:
        dob_value = str(dob).strip()

    dob_group = page.locator(
        ".oxd-input-group"
    ).filter(
        has_text="Date of Birth"
    )

    dob_input = dob_group.locator("input")

    dob_input.wait_for(state="visible")
    dob_input.fill(dob_value)

    print("Date of Birth entered successfully")


# ==========================================================
# BLOOD TYPE 
# ==========================================================

def fill_dropdown(page, label, value):
    print(f"Selecting {label}: {value}")

    # Find the input group containing the label
    group = page.locator(".oxd-input-group").filter(
        has=page.locator("label", has_text=label)
    )

    # Click dropdown
    group.locator(".oxd-select-text").click()

    # Select option
    page.locator(".oxd-select-option").filter(
        has_text=str(value).strip()
    ).click()

    print(f"{label} selected successfully")




def upload_document(page, employee):

    # ---------------------------------------------
    # Documents folder
    # ---------------------------------------------

            print("\n" + "-" * 40)
            print("Uploading employee document")
            print("-" * 40)

            first_name = str(employee["First Name"]).strip()
            last_name = str(employee["Last Name"]).strip()

            base_dir = Path(__file__).resolve().parent
            documents_dir = base_dir / "documents"

            

            # ---------------------------------------------
            # Read PDF filename from Excel
            # ---------------------------------------------
            document_name = str(employee["Document"]).strip()
            print(f"Document from Excel: {document_name}")

            document_path = documents_dir / f"{first_name}_{last_name}.pdf"

            print("\nDocument path:")
            print(document_path)

            # Check PDF exists
            if not document_path.exists():
                raise FileNotFoundError(
                    f"Document not found: {document_path}"
                )

            print("PDF found")
            print(f"File: {document_path.name}")

            # ---------------------------------------------
            # 1. Click Attachments section
            # ---------------------------------------------
            print("\nFinding Attachments section...")

            attachments = page.locator(
                ".orangehrm-attachment"
            )

            attachments.wait_for(
                state="visible",
                timeout=15000
            )

            print("Attachments section found")

            # ---------------------------------------------
            # 2. Click Add button
            # ---------------------------------------------

            print("Clicking Add...")

            add_button = attachments.get_by_role(
                "button",
                name="Add",
                exact=True
            )

            add_button.wait_for(
                state="visible",
                timeout=10000
            )

            add_button.click()

            print("Add Attachment form opened")


            # ---------------------------------------------
            # 3. Find file input
            # ---------------------------------------------
            file_input = page.locator(
                'input[type="file"].oxd-file-input'
            ).last

            file_input.wait_for(
                state="attached",
                timeout=10000
            )


            # ---------------------------------------------
            # 4. Upload PDF
            # ---------------------------------------------
            print("\nUploading PDF...")

            file_input.set_input_files(
                str(document_path)
            )

            print(f"PDF uploaded: {document_path.name}")

            # ---------------------------------------------
            # 5. Find attachment form
            # ---------------------------------------------
            attachment_form = page.locator(
                "form.oxd-form"
            ).filter(
                has=page.locator(
                    'input[type="file"].oxd-file-input'
                )
            ).last

            attachment_form.wait_for(
                state="visible",
                timeout=10000
            )

            # ---------------------------------------------
            # 6. Click Save
            # ---------------------------------------------
            print("Saving attachment...")

            save_button = attachment_form.get_by_role(
                "button",
                name="Save",
                exact=True
            )

            save_button.click()

            print("Attachment saved successfully")
