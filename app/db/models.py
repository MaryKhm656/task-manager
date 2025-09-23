from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.database import Base

task_categories_association = Table(
    "task_categories",
    Base.metadata,
    Column(
        "task_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "category_id",
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(256), nullable=False)
    is_admin = Column(Boolean, default=False)

    tasks = relationship("Task", back_populates="user", passive_deletes=True)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    deadline = Column(DateTime, nullable=True)
    status = Column(String(15), default="не выполнена")
    priority = Column(String(10), default="средний")

    user = relationship("User", back_populates="tasks")
    categories = relationship(
        "Category", secondary=task_categories_association, back_populates="tasks"
    )


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)

    tasks = relationship(
        "Task", secondary=task_categories_association, back_populates="categories"
    )
