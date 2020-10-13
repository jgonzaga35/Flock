from test_helpers import register_n_users
from user import user_profile
from error import InputError, AccessError
import pytest

from auth import auth_register


def test_user_profile_successful():

    user = register_n_users(1)  # return a user which has profile below:
    #                 email: email1@gmail.com",
    #                 passworkd: passwordthatislongenough1
    #                 first name: first1
    #                 last name: last1
    userProfile = user_profile(user["token"], user["id"])
    assert userProfile["email"] == "email1@gmail.com"
    assert userProfile["name_first"] == "first1"
    assert userProfile["name_last"] == "last1"


def test_user_profile_with_invalid_uid():
    """
    Testing when there is a user requesting for an user with
    invalid user id.

    We assume it raising InputError
    """
    user_a = register_n_users(1)
    # Generate a invalid user id for testing
    invalid_id = -1
    with pytest.raises(InputError):
        user_profile(user_a["token"], invalid_id)


def test_invalid_token_user_profile():
    """
    When a user with invalid token request for user profile

    We assume it raising AccessError
    """
    user_a = register_n_users(1)
    # Generate an invalid token
    invalid_token = "HaHa"
    with pytest.raises(AccessError):
        user_profile(invalid_token, user_a["u_id"])
