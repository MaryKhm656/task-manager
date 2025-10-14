import pytest

from app.services.user_service import UserService
from tests.constants.data import AccountParameters, MessageForCheck


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


def test_delete_account(create_default_test_user):
    """
    Scenario

    1. Create default test user
    2. Delete user from database
    3. Check success deleting user
    """
    db, user = create_default_test_user
    success_message = UserService.delete_user(db, user.id)
    assert (
        success_message == MessageForCheck.USER_SUCCESS_DELETE
    ), f"WARNING! {success_message} not equal to {MessageForCheck.USER_SUCCESS_DELETE}"
    with pytest.raises(ValueError, match=MessageForCheck.USER_NOT_FOUND):
        UserService.delete_user(db, user.id)
