import pytest
from user import users_all
from database import clear_database
from error import InputError, AccessError
from test_helpers import register_n_users, get_user_details


def test_users_all_single():
    clear_database()
    
    user = register_n_users(1)

    all_users = users_all(user["token"])
    all_users_info = []
    all_users_info.append(get_user_details(database["users"][1]))
    assert all_users == all_users_info
    
def test_users_all_many_users():
    clear_database()

    users = register_n_users(100)
    valid_token = users[1]["token"]
    all_users = users_all(valid_token)

    all_users_info = []
    for user in database["users"].values():
        all_users_info.append(get_user_details(user))

    assert all_users == all_users_info

def test_users_all_invalid_token():
    clear_database()
    with pytest.raises(AccessError):
        users_all(-1)
