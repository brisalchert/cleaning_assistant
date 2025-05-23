from PyQt6.QtCore import QSettings
from cryptography.fernet import Fernet
import os

key_path = os.path.expanduser("~\\.db_key")

def generate_and_store_key():
    if not os.path.exists(key_path):
        key = Fernet.generate_key()
        with open(key_path, "wb") as key_file:
            key_file.write(key)

def load_key():
    with open(key_path, "rb") as key_file:
        return key_file.read()

def encrypt_data(data: str, key: bytes) -> str:
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data.encode())
    return encrypted.decode()

def decrypt_data(encrypted_data: str, key: bytes) -> str:
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted_data.encode())
    return decrypted.decode()

def save_encrypted_db_credentials(db_name: str, user: str, host: str, password: str, port: int, key: bytes):
    settings = QSettings("CleaningAssistant", "CleaningAssistant")
    settings.setValue("db_name", encrypt_data(db_name, key))
    settings.setValue("user", encrypt_data(user, key))
    settings.setValue("host", encrypt_data(host, key))
    settings.setValue("password", encrypt_data(password, key))
    settings.setValue("port", encrypt_data(str(port), key))

def delete_saved_db_credentials():
    settings = QSettings("CleaningAssistant", "CleaningAssistant")
    settings.clear()

def load_encrypted_db_credentials(key: bytes):
    settings = QSettings("CleaningAssistant", "CleaningAssistant")

    # Look for encrypted credentials
    encrypted_db_name = settings.value("db_name", "", type=str)
    encrypted_user = settings.value("user", "", type=str)
    encrypted_host = settings.value("host", "", type=str)
    encrypted_password = settings.value("password", "", type=str)
    encrypted_port = settings.value("port", "", type=str)

    if all([encrypted_db_name, encrypted_user, encrypted_host, encrypted_password, encrypted_port]):
        connection_details = {
            "db_name": decrypt_data(encrypted_db_name, key),
            "user": decrypt_data(encrypted_user, key),
            "host": decrypt_data(encrypted_host, key),
            "password": decrypt_data(encrypted_password, key),
            "port": int(decrypt_data(encrypted_port, key))
        }

        return connection_details
    else:
        return None
