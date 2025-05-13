import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status,Request
from fastapi.security import OAuth2PasswordBearer
from app.db.models import User
from app.db.database import SessionLocal
from app.crud.security import verify_password

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict, expires_delta: timedelta=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credential_exception = HTTPException(
        status_code=401,
        detail="Не удалось проверить токен",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credential_exception
    except JWTError:
        raise credential_exception
    
    session = SessionLocal()
    user = session.query(User).filter_by(id=user_id).first()
    session.close()
    if user is None:
        raise credential_exception
    return user


def login_user(email: str, password: str):
    session = SessionLocal()
    user = session.query(User).filter_by(email=email).first()
    session.close()
    
    if user is None or not verify_password(password, user.password):
        raise ValueError("Неверный email или пароль")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return access_token


def admin_required(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Данные действия доступны только администратору"
        )
    return current_user


def get_current_user_from_cookie(request: Request) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Токен не найден в cookie")
    
    credential_exception = HTTPException(status_code=401, detail="Не удалось проверить токен", headers={"WWW-Authenticate": "Bearer"})
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credential_exception
    except JWTError:
        raise credential_exception
    
    session = SessionLocal()
    user = session.query(User).filter_by(id=user_id).first()
    session.close()
    
    if user is None:
        raise credential_exception
    
    return user