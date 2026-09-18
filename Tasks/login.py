import tkinter as tk
from tkinter import messagebox
import configparser


def get_login_credentials():

    # -------------------------
    # Read config.ini
    # -------------------------

    config = configparser.ConfigParser()

    config.read("config.ini")

    username = config["ORANGEHRM"]["username"]
    password = config["ORANGEHRM"]["password"]

    # -------------------------
    # Submit function
    # -------------------------

    def submit():

        nonlocal username
        nonlocal password

        username = username_entry.get()
        password = password_entry.get()

        if username == "" or password == "":
            messagebox.showwarning(
                "Warning",
                "Please enter Username and Password"
            )
            return

        root.destroy()

    # -------------------------
    # Tkinter window
    # -------------------------

    root = tk.Tk()

    root.title("OrangeHRM Login")
    root.geometry("350x200")

    # -------------------------
    # Username
    # -------------------------

    tk.Label(
        root,
        text="Username"
    ).pack(pady=5)

    username_entry = tk.Entry(root)
    username_entry.pack()

    # Fill username from config.ini
    username_entry.insert(
        0,
        username
    )

    # -------------------------
    # Password
    # -------------------------

    tk.Label(
        root,
        text="Password"
    ).pack(pady=5)

    password_entry = tk.Entry(
        root,
        show="*"
    )

    password_entry.pack()

    # Fill password from config.ini
    password_entry.insert(
        0,
        password
    )


    tk.Button(
        root,
        text="Login",
        command=submit
    ).pack(pady=15)

    root.mainloop()

    return username, password