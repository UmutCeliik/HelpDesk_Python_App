# auth_service/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
import httpx # httpx'i import et

from .auth import AuthHandler

app = FastAPI(title="Authentication Service API")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")



# User Service'in URL'si (Normalde konfigürasyondan/ortam değişkeninden alınmalı)
USER_SERVICE_URL = "http://127.0.0.1:8001"

origins = [
    "http://localhost:5173",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost", # Bazen sadece localhost gerekebilir
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # İzin verilen kaynaklar (frontend adresleri)
    allow_credentials=True, # Cookie veya Authorization header gibi bilgilerin gönderilmesine izin ver
    allow_methods=["*"], # İzin verilen HTTP metotları (GET, POST, PUT, DELETE vb. hepsi)
    allow_headers=["*"], # İzin verilen HTTP başlıkları (Authorization, Content-Type vb. hepsi)
)

@app.get("/")
async def read_root():
    return {"message": "Authentication Service API'ye hoş geldiniz!"}


@app.post("/auth/token", summary="Kullanıcı Girişi Yap ve Token Al")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    # 1. User Service'den kullanıcıyı e-postasına göre al
    user_data = None
    async with httpx.AsyncClient() as client:
        try:
            # User Service'deki dahili endpoint'e istek at
            response = await client.get(
                f"{USER_SERVICE_URL}/users/internal/by_email/{form_data.username}"
            )
            response.raise_for_status() # HTTP 4xx veya 5xx hatası varsa exception fırlat
            user_data = response.json() # Yanıtı JSON olarak al

        except httpx.HTTPStatusError as exc:
            # Kullanıcı bulunamadı (404) veya başka bir istemci hatası
            if exc.response.status_code == 404:
                print(f"User Service 404 hatası verdi: {form_data.username} bulunamadı.")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="E-posta veya şifre hatalı",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                # User service'den beklenmedik bir hata
                print(f"User Service Hata Kodu: {exc.response.status_code}")
                print(f"User Service Yanıtı: {exc.response.text}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Kimlik doğrulama sırasında bir sorun oluştu.",
                )
        except httpx.RequestError as exc:
            # User service'e bağlanılamadı
            print(f"User Service'e bağlanılamadı: {exc}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Kimlik doğrulama servisi şu anda kullanılamıyor.",
            )

    # 2. Şifreyi doğrula (User Service'den gelen hash ile)
    if not user_data or not AuthHandler.verify_password(form_data.password, user_data["hashed_password"]):
         print(f"Şifre doğrulama başarısız: Kullanıcı={form_data.username}")
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-posta veya şifre hatalı",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Kullanıcının aktif olup olmadığını da kontrol edebiliriz (User Service'den geliyorsa)
    if not user_data.get("is_active", True): # is_active yoksa True varsayalım
        print(f"Kullanıcı aktif değil: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hesap aktif değil"
        )

    # 3. Erişim Token'ı Oluştur
    access_token_data = {
        "sub": user_data["email"],
        "user_id": user_data["id"], # User Service'den gelen ID
        "role": user_data["role"]  # User Service'den gelen rol
    }
    access_token = AuthHandler.create_access_token(data=access_token_data)

    # 4. Token'ı Döndür
    return {"access_token": access_token, "token_type": "bearer"}
# --- Korunmuş Örnek Endpoint (Token Doğrulama Testi İçin) ---
# Bu endpoint Auth Service'in kendisinde olmak zorunda değil,
# genelde diğer servislerde (Ticket, User vb.) olur.
# Sadece token doğrulamanın nasıl çalıştığını göstermek için ekledik.

# @app.get("/auth/me", summary="Mevcut Kullanıcı Bilgisini Getir (Token Gerekli)")
# async def read_users_me(token: Annotated[str, Depends(oauth2_scheme)]):
#     """
#     Geçerli bir Bearer token ile çağrıldığında token içeriğini döndürür.
#     """
#     payload = AuthHandler.decode_token(token)
#     if payload is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Geçersiz veya süresi dolmuş token",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     # Gerçekte burada payload içindeki user_id ile User Service'den
#     # güncel kullanıcı bilgilerini çekmek daha doğru olur.
#     return payload