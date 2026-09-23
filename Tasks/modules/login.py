import tkinter as tk

from config.config_reader import get_login_credentials


def get_login_credentials_from_popup():

    # Get default credentials from config.ini
    username, password = get_login_credentials()

    result = {
        "username": None,
        "password": None,
        "login_clicked": False
    }

    root = tk.Tk()
    root.title("OrangeHRM Bot Login")

    window_width = 400
    window_height = 220

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    root.geometry(
        f"{window_width}x{window_height}+{x}+{y}"
    )

    root.resizable(False, False)

    # Title
    tk.Label(
        root,
        text="OrangeHRM Login",
        font=("Arial", 16, "bold")
    ).pack(pady=15)

    # Username
    tk.Label(
        root,
        text="Username"
    ).pack()

    username_entry = tk.Entry(
        root,
        width=35
    )
    username_entry.pack()

    username_entry.insert(
        0,
        username
    )

    # Password
    tk.Label(
        root,
        text="Password"
    ).pack(pady=(10, 0))

    password_entry = tk.Entry(
        root,
        width=35,
        show="*"
    )
    password_entry.pack()

    password_entry.insert(
        0,
        password
    )

    # Login button
    def login_clicked():

        result["username"] = username_entry.get().strip()
        result["password"] = password_entry.get().strip()
        result["login_clicked"] = True

        root.destroy()

    tk.Button(
        root,
        text="Login",
        width=15,
        command=login_clicked
    ).pack(pady=15)

    root.mainloop()

    # If user closes popup without clicking Login
    if not result["login_clicked"]:
        return None, None

    return result["username"], result["password"]

def login(page, username, password, url):

    page.goto(url)

    page.get_by_placeholder("Username").fill(username)

    page.get_by_placeholder("Password").fill(password)

    page.get_by_role(
        "button",
        name="Login"
    ).click()

    page.wait_for_load_state("networkidle")