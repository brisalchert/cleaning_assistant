import os
import tempfile
import shutil
import pytest
from unittest.mock import patch, MagicMock
from cryptography.fernet import Fernet
from utils import *


@pytest.fixture
def temp_key_path(monkeypatch):
    # Create a temporary directory to hold the key file
    temp_dir = tempfile.mkdtemp()
    temp_key = os.path.join(temp_dir, "db_key_test")
    monkeypatch.setattr(security, "key_path", temp_key)
    yield temp_key
    shutil.rmtree(temp_dir)

def test_generate_and_store_key_creates_key(temp_key_path):
    # The file shouldn't exist yet
    assert not os.path.exists(temp_key_path)
    generate_and_store_key()
    assert os.path.exists(temp_key_path)
    with open(temp_key_path, "rb") as f:
        key = f.read()
    assert len(key) == 44  # Fernet keys are 44 bytes base64

def test_generate_and_store_key_does_not_overwrite(temp_key_path):
    generate_and_store_key()
    with open(temp_key_path, "rb") as f:
        original_key = f.read()
    generate_and_store_key()
    with open(temp_key_path, "rb") as f:
        new_key = f.read()
    assert original_key == new_key

def test_load_key_returns_key(temp_key_path):
    generate_and_store_key()
    loaded_key = load_key()
    with open(temp_key_path, "rb") as f:
        original_key = f.read()
    assert loaded_key == original_key

def test_encrypt_decrypt_roundtrip():
    key = Fernet.generate_key()
    plaintext = "Hello, World!"
    encrypted = encrypt_data(plaintext, key)
    decrypted = decrypt_data(encrypted, key)
    assert decrypted == plaintext

@patch("utils.security.QSettings")
def test_save_and_load_encrypted_db_credentials(mock_qsettings, temp_key_path):
    # Setup
    key = Fernet.generate_key()
    settings_instance = MagicMock()
    mock_qsettings.return_value = settings_instance

    db_name = "test_db"
    user = "user1"
    host = "localhost"
    password = "password123"
    port = 5432

    # Save credentials (check encrypt_data is called correctly by side effect)
    save_encrypted_db_credentials(db_name, user, host, password, port, key)

    # Check that setValue was called with encrypted data
    calls = [call[0] for call in settings_instance.setValue.call_args_list]
    keys = {"db_name", "user", "host", "password", "port"}
    called_keys = {k for k, v in calls}
    assert keys == called_keys

    # Set up the return values for settings.value to simulate stored encrypted values
    def side_effect_value(k, default, type):
        # Return encrypted value corresponding to the key
        mapping = {
            "db_name": encrypt_data(db_name, key),
            "user": encrypt_data(user, key),
            "host": encrypt_data(host, key),
            "password": encrypt_data(password, key),
            "port": encrypt_data(str(port), key),
        }
        return mapping.get(k, "")

    settings_instance.value.side_effect = side_effect_value

    # Load credentials and check correctness
    creds = load_encrypted_db_credentials(key)
    assert creds == {
        "db_name": db_name,
        "user": user,
        "host": host,
        "password": password,
        "port": port,
    }

@patch("utils.security.QSettings")
def test_delete_saved_db_credentials(mock_qsettings):
    settings_instance = MagicMock()
    mock_qsettings.return_value = settings_instance

    delete_saved_db_credentials()

    settings_instance.clear.assert_called_once()
