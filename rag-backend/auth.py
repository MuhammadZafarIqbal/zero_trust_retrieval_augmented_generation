from fastapi import Depends, HTTPException, Header
from jose import jwt
import httpx
from jose.utils import base64url_decode
from jose.exceptions import JWTError
from jose import jwk
import json

MICROSOFT_KEYS_URL = "https://login.microsoftonline.com/common/discovery/v2.0/keys"
AUDIENCE = f"api://6e3a0f77-a606-43cd-83ab-6b9181b1222f"

# Cache the keys in memory (simplest approach)
JWKS_CACHE = None

async def get_jwks():
    global JWKS_CACHE
    if JWKS_CACHE is None:
        async with httpx.AsyncClient() as client:
            resp = await client.get(MICROSOFT_KEYS_URL)
            resp.raise_for_status()
            JWKS_CACHE = resp.json()["keys"]
    return JWKS_CACHE

async def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    token = authorization[7:]
    jwks = await get_jwks()

    # Decode unverified header to get 'kid'
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")
    if not kid:
        raise HTTPException(status_code=401, detail="Missing kid in token header")

    key_data = next((k for k in jwks if k["kid"] == kid), None)
    if not key_data:
        raise HTTPException(status_code=401, detail="Unknown kid")
    
    if "alg" not in key_data:
        key_data["alg"] = "RS256"
    
    # Parse JWK
    public_key = jwk.construct(key_data)

    message, encoded_signature = str(token).rsplit('.', 1)
    decoded_signature = base64url_decode(encoded_signature.encode())

    if not public_key.verify(message.encode(), decoded_signature):
        raise HTTPException(status_code=401, detail="Invalid token signature")

    # Validate claims
    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=AUDIENCE
        )
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=str(e))