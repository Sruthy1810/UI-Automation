from configparser import RawConfigParser
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config.ini"


config = RawConfigParser()
config.read(CONFIG_FILE)


def get_orangehrm_url():
    url =  config["ORANGEHRM"]["URL"]
    return url


def get_login_credentials():
    username = config["ORANGEHRM"]["USERNAME"]
    password = config["ORANGEHRM"]["PASSWORD"]

    return username, password


def get_employee_file_path():
    file_path = config["FILES"]["employee_excel"]

    return BASE_DIR / file_path


def get_assets_folder():
    return BASE_DIR / config["FILES"]["ASSETS_FOLDER"]


def get_documents_folder():
    return BASE_DIR / config["FILES"]["DOCUMENTS_FOLDER"]


def get_screenshot_folder():
    return BASE_DIR / config["FILES"]["SCREENSHOT_FOLDER"]


def get_email_config():
    return {
        "smtp_server": config["EMAIL"]["SMTP_SERVER"],
        "smtp_port": int(config["EMAIL"]["SMTP_PORT"]),
        "sender_email": config["EMAIL"]["SENDER_EMAIL"],
        "sender_password": config["EMAIL"]["SENDER_PASSWORD"],
        "receiver_email": config["EMAIL"]["RECEIVER_EMAIL"],
    }