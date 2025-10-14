import os
import sys

from app.dependencies import get_db

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.models import User


def make_admin(email: str):
    db = get_db()
    user = db.query(User).filter_by(email=email).first()

    if user:
        user.is_admin = True
        db.commit()
        print(f"{email} теперь администратор!")
    else:
        print(f"Пользователь {email} не найден")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python make_admin.py <username>")
        sys.exit(1)

    email = sys.argv[1]
    make_admin(email)
