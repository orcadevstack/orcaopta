from cryptography.fernet import Fernet, MultiFernet
import os

def load_keys():
    """
    Load Fernet keys from environment variables or Kubernetes secrets.
    Example:
      export FERNET_KEYS="key1,key2,key3"
    """
    raw = os.getenv("FERNET_KEYS")
    if not raw:
        raise RuntimeError("FERNET_KEYS not set")

    keys = raw.split(",")
    fernets = [Fernet(k.encode()) for k in keys]
    return MultiFernet(fernets)

f = load_keys()

def encrypt(data: bytes) -> bytes:
    return f.encrypt(data)

def decrypt(token: bytes) -> bytes:
    return f.decrypt(token)

def rotate(token: bytes) -> bytes:
    return f.rotate(token)
