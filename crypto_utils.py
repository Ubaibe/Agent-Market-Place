from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()

ENCRYPTION_KEY = os.getenv("MEMORY_ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    raise ValueError("Missing MEMORY_ENCRYPTION_KEY")

cipher = Fernet(ENCRYPTION_KEY.encode())

def encrypt_text(text: str) -> str:
    return cipher.encrypt(text.encode()).decode()

def decrypt_text(encrypted_text: str) -> str:
    return cipher.decrypt(encrypted_text.encode()).decode()
