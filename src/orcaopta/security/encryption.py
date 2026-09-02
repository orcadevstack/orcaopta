import os
import json
from typing import Union
from cryptography.fernet import Fernet, InvalidToken

def _load_master_key() -> Fernet:
    master_key = os.getenv("ORCAOPTA_MASTER_KEY")
    if not master_key:
        raise RuntimeError("ORCAOPTA_MASTER_KEY is missing")
    return Fernet(master_key.encode())

def _load_data_key(env_name: str) -> Fernet:
    encrypted_key = os.getenv(env_name)
    if not encrypted_key:
        raise RuntimeError(f"{env_name} is missing")
    master = _load_master_key()
    decrypted = master.decrypt(encrypted_key.encode())
    return Fernet(decrypted)

class EncryptionService:
    def encrypt(self, key_name: str, data: Union[str, bytes]) -> bytes:
        f = _load_data_key(key_name)
        if isinstance(data, str):
            data = data.encode("utf-8")
        return f.encrypt(data)

    def decrypt(self, key_name: str, token: Union[str, bytes]) -> bytes:
        f = _load_data_key(key_name)
        if isinstance(token, str):
            token = token.encode("utf-8")
        try:
            return f.decrypt(token)
        except InvalidToken as e:
            raise InvalidToken("Decryption failed: invalid token or key") from e

    def encrypt_dict(self, key_name: str, data: dict) -> bytes:
        return self.encrypt(key_name, json.dumps(data))

    def decrypt_dict(self, key_name: str, token: Union[str, bytes]) -> dict:
        raw = self.decrypt(key_name, token)
        return json.loads(raw.decode())

    def generate_data_key(self) -> str:
        master = _load_master_key()
        raw = Fernet.generate_key()
        encrypted = master.encrypt(raw)
        return encrypted.decode()

def encrypt(data: Union[str, bytes]) -> str:
    svc = EncryptionService()
    token = svc.encrypt("ORCAOPTA_DB_KEY", data)
    return token.decode("utf-8")

def decrypt(token: Union[str, bytes]) -> str:
    svc = EncryptionService()
    raw = svc.decrypt("ORCAOPTA_DB_KEY", token)
    return raw.decode("utf-8")

def encrypt_dict(data: dict) -> str:
    svc = EncryptionService()
    token = svc.encrypt_dict("ORCAOPTA_DB_KEY", data)
    return token.decode("utf-8")

def decrypt_dict(token: Union[str, bytes]) -> dict:
    svc = EncryptionService()
    raw = svc.decrypt_dict("ORCAOPTA_DB_KEY", token)
    return raw
