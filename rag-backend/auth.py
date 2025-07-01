from fastapi import Depends, HTTPException, Header
from jose import jwt
import httpx

MICROSOFT_KEYS_URL = "https://login.microsoftonline.com/common/discovery/v2.0/keys"
AUDIENCE = "6e3a0f77-a606-43cd-83ab-6b9181b1222f"

async def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    token = authorization[7:]
    async with httpx.AsyncClient() as client:
        keys = (await client.get(MICROSOFT_KEYS_URL)).json()["keys"]

    for key in keys:
        try:
            public_key = jwt.construct_rsa_public_key(key)
            payload = jwt.decode(token, public_key, algorithms=["RS256"], audience=AUDIENCE)
            return payload
        except Exception:
            continue

    raise HTTPException(status_code=401, detail="Invalid token")
