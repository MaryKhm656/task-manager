from sqlalchemy.orm import Session

from app.crud.security import hash_password, verify_password
from app.db.models import User


class UserService:
    @staticmethod
    def create_user(db: Session, name: str, email: str, password: str) -> User:
        """Method for create new user in DB with validate data"""
        if len(name) < 2:
            raise ValueError("Имя пользователя не может быть меньше двух символов")

        if "@" not in email or "." not in email:
            raise ValueError("Некорректный email")

        existing_user = db.query(User).filter_by(email=email).first()
        if existing_user:
            raise ValueError("Аккаунт с таким email уже существует!")

        hashed_pwd = hash_password(password)
        user = User(name=name.strip(), email=email, password=hashed_pwd)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def login_user(db: Session, email: str, password: str) -> type[User] | None:
        """Method for login user with validate data"""
        user = db.query(User).filter_by(email=email).first()
        if not user or not verify_password(password, user.password):
            raise ValueError("Неверный email или пароль")
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> str:
        """Method for deleting user"""
        user = db.get(User, user_id)
        if not user:
            raise ValueError("Пользователь с таким ID не найден")
        db.delete(user)
        db.commit()
        return "Пользователь успешно удален"
