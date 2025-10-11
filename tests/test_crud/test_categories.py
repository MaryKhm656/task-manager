from app.services.category_service import CategoryService
from tests.constants.data import CategoryParameters


def test_create_categories(init_db):
    """
    Scenario

    1. Create categories
    2. Check categories created
    """
    db = init_db
    category = CategoryService.create_category(db, CategoryParameters.HOME)
    assert (
        category.title == CategoryParameters.HOME
    ), f"{category.title} not equal to {CategoryParameters.HOME}"


def test_getting_all_categories(data_for_test):
    """
    Scenario

    1. Getting all categories from database
    2. Check categories getting
    """
    _, _, db = data_for_test
    categories_from_db = CategoryService.get_all_categories(db)
    assert CategoryParameters.ALL_CATEGORIES == [
        category.title for category in categories_from_db
    ], (
        f"{CategoryParameters.ALL_CATEGORIES} not equal to "
        f"{[category.title for category in categories_from_db]}"
    )
