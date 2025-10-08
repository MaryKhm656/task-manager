from app.db.database import init_db
from app.db.models import (  # noqa: F401
    Category,
    Task,
    User,
    task_categories_association,
)

if __name__ == "__main__":
    init_db()
