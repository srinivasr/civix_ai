from fastapi import Security
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_current_user(api_key: str = Security(api_key_header)):
    """
    Mock implementation of role-based access control.
    """
    if api_key == "dev-secret":
        return {"username": "admin", "role": "admin"}
    # Return a generic guest or raise exception depending on strictness
    return {"username": "guest", "role": "guest"}
