from typing import List

from sqlalchemy.orm import Session

from app.db.models import Category


class CategoryService:
    @staticmethod
    def create_category(db: Session, title: str) -> Category:
        """Create new category with validate data"""
        clean_title = title.lower().strip()
        if not clean_title:
            raise ValueError("Название категории не может быть пустым")

        existing = db.query(Category).filter_by(title=clean_title).first()
        if existing:
            raise ValueError("Такая категория уже существует")

        category = Category(title=clean_title)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def get_all_categories(db: Session) -> List[Category]:
        """Getting all categories"""
        return db.query(Category).all()

    @staticmethod
    def delete_category(db: Session, category_id: int) -> str:
        """
        Deleting category and return success message
        or raise ValueError if category not found in DB
        """
        category = db.get(Category, category_id)
        if not category:
            raise ValueError("Категория с таким ID не найдена")
        db.delete(category)
        db.commit()
        return "Категория успешно удалена"

    @staticmethod
    def delete_categories_list(db: Session, categories_ids: list[int]) -> str:
        """Deleting list categories and return success message or raise ValueError"""
        for category_id in categories_ids:
            category = db.get(Category, category_id)
            if not category:
                raise ValueError(f"Категория с {category_id} не найдена")
            db.delete(category)
        db.commit()
        return "Категории успешно удалены"
