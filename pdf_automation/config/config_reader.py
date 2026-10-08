import configparser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = r"C:/config/pdf_automation.txt"

config = configparser.ConfigParser()
config.read(CONFIG_FILE)


def pdf_file():
    return str(BASE_DIR / config["FILES"]["pdf_file"])