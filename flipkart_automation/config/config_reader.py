from configparser import RawConfigParser
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config.ini"

config = RawConfigParser()

config_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "config.ini"
)

config.read(config_path)


def get_flipkart_url():
    url = config["FLIPKART"]["URL"]
    return url

def get_login_type():
    return config["FLIPKART"]["LOGIN_TYPE"]

def get_phonenumber():
    phone_number = config["FLIPKART"]["Phone_number"]
    return phone_number

def get_email():
    mail = config["FLIPKART"]["email"]
    return mail

def get_product_file():
    return Path(config["FILES"]["product_excel"])
    

def get_session_file():
    session_file = config["FILES"]["SESSION_FILE"]  
    return Path(session_file)      

def get_smtp_server():
    return config["EMAIL"]["smtp_server"]


def get_smtp_port():
    return int(config["EMAIL"]["smtp_port"])


def get_sender_email():
    return config["EMAIL"]["sender_email"]


def get_sender_password():
    return config["EMAIL"]["sender_password"]


def get_receiver_email():
    return config["EMAIL"]["receiver_email"]