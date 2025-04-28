# auth_service/auth.py
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Any
from jose import jwt, JWTError
from passlib.context import CryptContext # Şifre doğrulaması için (User Service ile aynı olmalı)

# Şifreleme bağlamı (User Service'deki ile aynı olmalı)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- JWT Ayarları ---
# !!! GÜVENLİK UYARISI: Bu anahtarı ASLA kod içinde sabit bırakmayın!
# Ortam değişkenlerinden veya bir sır yönetim aracından yükleyin.
SECRET_KEY = "cok-gizli-bir-anahtar-buraya-gelecek"
ALGORITHM = "HS256" # Kullandığımız imzalama algoritması
ACCESS_TOKEN_EXPIRE_MINUTES = 1 # Erişim token'ının geçerlilik süresi (dakika)

class AuthHandler:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Düz metin şifre ile hashlenmiş şifreyi karşılaştırır."""
        # Gerçekte hashlenmiş şifre User Service'den gelecek.
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Düz metin şifreyi hashler (Bu aslında User Service'in işi)."""
        # Bu fonksiyonu burada sadece test/simülasyon için tutabiliriz.
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Verilen veri ve süreye göre bir JWT Erişim Token'ı oluşturur."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            # Varsayılan süre
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire}) # Son kullanma tarihini ekle
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Bir JWT token'ını doğrular ve içeriğini (payload) çözer."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            # Token geçersiz veya süresi dolmuş olabilir
            return None