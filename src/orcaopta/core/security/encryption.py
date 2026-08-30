import base64
import os
from typing import Union

from cryptography.fernet import Fernet, InvalidToken



def _load_key_from_env() -> bytes:
    """
    Load the Orcaopta encryption key from environment.
    If not present, generate a new one (for ephemeral/local use).
    In production, you should ALWAYS set ORCAOPTA_ENCRYPTION_KEY.
    """
    key_str = os.getenv("ORCAOPTA_ENCRYPTION_KEY")

    if key_str:
        # Allow raw Fernet key or base64-encoded
        try:
            return key_str.encode("utf-8")
        except Exception:
            raise ValueError("Invalid ORCAOPTA_ENCRYPTION_KEY format")

    # Fallback: generate a new key (not persisted!)
    key = Fernet.generate_key()
    return key


def get_fernet() -> Fernet:
    """
    Return a Fernet instance using the configured key.
    """
    key = _load_key_from_env()
    return Fernet(key)




def encrypt(plaintext: Union[str, bytes]) -> str:
    """
    Encrypt a string/bytes and return a base64-encoded token (str).
    """
    f = get_fernet()

    if isinstance(plaintext, str):
        plaintext_bytes = plaintext.encode("utf-8")
    else:
        plaintext_bytes = plaintext

    token = f.encrypt(plaintext_bytes)
    # Return as UTF-8 string
    return token.decode("utf-8")


def decrypt(token: Union[str, bytes]) -> str:
    """
    Decrypt a token (str/bytes) and return the original string.
    Raises InvalidToken if the key is wrong or data is corrupted.
    """
    f = get_fernet()

    if isinstance(token, str):
        token_bytes = token.encode("utf-8")
    else:
        token_bytes = token

    try:
        plaintext_bytes = f.decrypt(token_bytes)
    except InvalidToken as e:
        raise InvalidToken("Decryption failed: invalid token or key") from e

    return plaintext_bytes.decode("utf-8")



def encrypt_dict(data: dict) -> str:
    """
    Encrypt a dict by JSON-encoding then encrypting.
    """
    import json
    return encrypt(json.dumps(data))


def decrypt_dict(token: Union[str, bytes]) -> dict:
    """
    Decrypt a token into a dict.
    """
    import json
    return json.loads(decrypt(token))
