from configparser import ConfigParser
from pathlib import Path


CONFIG_FILE = r"C:/config/Flipkart_automation.txt"
config = ConfigParser()

config.read(CONFIG_FILE)


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

def get_log_folder():
    return Path(config["FILES"]["LOG_FOLDER"])

def get_cart_url():
    return config["FLIPKART"]["CART_URL"]

def get_max_products():
    try:
        value = int(config["SETTINGS"]["max_products"])   # use your section/object names
        return max(1, value)                               # never less than 1
    except Exception:
        return 1  