import configparser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = r"C:/config/pdf_automation.txt"

config = configparser.ConfigParser()
config.read(CONFIG_FILE)


def get_pdf_files():
    input_folder = BASE_DIR / config["FILES"]["input_folder"]
    return sorted(input_folder.glob("*.pdf"))

def get_output_path():
    return BASE_DIR / config["FILES"]["output_file"]
