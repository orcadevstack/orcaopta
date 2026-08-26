from cryptography.fernet import Fernet, MultiFernet
import os

def load_keys():
    raw = os.getenv("FERNET_KEYS")
    if not raw:
        raise RuntimeError("FERNET_KEYS not set")

    keys = raw.split(",")
    fernets = [Fernet(k.encode()) for k in keys]
    return MultiFernet(fernets)

def encrypt(data: bytes) -> bytes:
    return load_keys().encrypt(data)

def decrypt(token: bytes) -> bytes:
    return load_keys().decrypt(token)

def rotate(token: bytes) -> bytes:
    return load_keys().rotate(token)
