# ticket_service/auth.py
from datetime import datetime, timezone, timedelta
from typing import Optional, Annotated
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "cok-gizli-bir-anahtar-buraya-gelecek" # Auth Service ile aynı olmalı
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://127.0.0.1:8002/auth/token")

class AuthHandler:
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError as e:
            print(f"Token decode hatası: {e}")
            return None

async def get_current_user_payload(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = AuthHandler.decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz kimlik bilgileri",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload