from test_helpers import register_n_users
from user import user_profile, user_profile_setname
from error import InputError, AccessError
import pytest
from database import clear_database, database
from auth import auth_register

# --------------------------------user profile-------------------------------------
def test_user_profile_successful():
    clear_database()
    user = register_n_users(1)  # return a user which has profile below:
    #                 email: email1@gmail.com",
    #                 passworkd: passwordthatislongenough1
    #                 first name: first1
    #                 last name: last1

    # We compare the profile above to the returned result.
    userProfile = user_profile(user["token"], user["u_id"])
    assert userProfile["email"] == "email0@gmail.com"
    assert userProfile["first_name"] == "first0"
    assert userProfile["last_name"] == "last0"


def test_user_profile_with_invalid_uid():
    """
    Testing when there is a user requesting for an user with
    invalid user id.

    We assume it raising InputError
    """
    clear_database()
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
    clear_database()
    user_a = register_n_users(1)
    # Generate an invalid token
    invalid_token = "HaHa"
    with pytest.raises(AccessError):
        user_profile(invalid_token, user_a["u_id"])


# -----------------------------user_profile_setname------------------------------
def test_setname_successful():
    clear_database()
    user_a = register_n_users(1)
    # set user name to Eric JOJO
    user_profile_setname(user_a["token"], "Eric", "JOJO")

    assert database["users"][user_a["u_id"]]["first_name"] == "Eric"
    assert database["users"][user_a["u_id"]]["last_name"] == "JOJO"


def test_setname_firstname_too_long():
    clear_database()
    user_a = register_n_users(1)
    with pytest.raises(InputError):
        # set user name to Erichahaha... JOJO
        # first name is too long
        user_profile_setname(
            user_a["token"],
            "Erichaahahahahahahahahahahahahahahahahahahahahahahahahahahahahahaa",
            "JOJO",
        )


def test_setname_lastname_too_long():
    clear_database()
    user_a = register_n_users(1)
    with pytest.raises(InputError):
        # set user name to Erichahaha... JOJO
        # first name is too long
        user_profile_setname(
            user_a["token"],
            "Eric",
            "JOJOahahahahahahahahahahahahahahahahahahahahahahahahahahahahaa",
        )


def test_setname_invalid_token():
    clear_database()
    user_a = register_n_users(1)
    # Generate an invalid token
    invalid_token = "HaHa"
    with pytest.raises(AccessError):
        user_profile_setname(invalid_token, "Eric", "JOJO")
