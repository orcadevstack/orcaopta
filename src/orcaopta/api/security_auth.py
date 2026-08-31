

from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
import jwt
import time

JWT_SECRET = "ORCAOPTA_SUPER_SECRET"
JWT_ALGO = "HS256"

bearer = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

class SecurityAuth:
    """
    Provides JWT + API key authentication for Orcaopta Security API.
    """

    # -------------------------------------------------------------
    # JWT generation
    # -------------------------------------------------------------
    def create_jwt(self, subject: str, expires_in: int = 3600):
        payload = {
            "sub": subject,
            "exp": int(time.time()) + expires_in,
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

    # -------------------------------------------------------------
    # JWT validation
    # -------------------------------------------------------------
    def validate_jwt(self, creds: HTTPAuthorizationCredentials = Security(bearer)):
        try:
            token = creds.credentials
            decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
            return decoded
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid or expired JWT")

    # -------------------------------------------------------------
    # API key validation
    # -------------------------------------------------------------
    def validate_api_key(self, api_key: str = Security(api_key_header)):
        if api_key != "ORCAOPTA_API_KEY":
            raise HTTPException(status_code=401, detail="Invalid API key")
        return {"api_key": api_key}
