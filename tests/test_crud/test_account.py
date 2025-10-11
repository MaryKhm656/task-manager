from app.services.user_service import UserService
from tests.constants.data import AccountParameters


def test_create_account(init_db):
    """
    Scenario

    1. Create account with default test data
    2. Check account was saved
    """
    db = init_db
    account = UserService.create_user(
        db=db,
        name=AccountParameters.USERNAME,
        email=AccountParameters.EMAIL,
        password=AccountParameters.PASSWORD,
    )
    assert (
        account.name == AccountParameters.USERNAME
    ), f"{account.name} not equal to {AccountParameters.USERNAME}"
    assert (
        account.email == AccountParameters.EMAIL
    ), f"{account.email} not equal to {AccountParameters.EMAIL}"
    UserService.delete_user(db, account.id)
