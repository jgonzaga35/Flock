from test_helpers import register_n_users
from user import (
    user_profile,
    user_profile_setname,
    user_profile_setemail,
    user_profile_sethandle,
)
from error import InputError, AccessError
import pytest
from database import clear_database
from auth import auth_register, check_email

# --------------------------------user profile-------------------------------------
def test_user_profile_successful():
    clear_database()
    user = register_n_users(1)  # return a user which has profile below:
    #                 email: email0@gmail.com",
    #                 first name: first0
    #                 last name: last0

    # We compare the profile above to the returned result.
    userProfile = user_profile(user["token"], user["u_id"])
    assert userProfile["email"] == "email0@gmail.com"
    assert userProfile["name_first"] == "first0"
    assert userProfile["name_last"] == "last0"


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
    user_a_profile = user_profile(user_a["token"], user_a["u_id"])
    assert user_a_profile["name_first"] == "Eric"
    assert user_a_profile["name_last"] == "JOJO"


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
        # last name is too long
        user_profile_setname(
            user_a["token"],
            "Eric",
            "JOJOahahahahahahahahahahahahahahahahahahahahahahahahahahahahaa",
        )


def test_setname_invalid_token():
    clear_database()
    # Generate an invalid token
    invalid_token = "HaHa"
    with pytest.raises(AccessError):
        user_profile_setname(invalid_token, "Eric", "JOJO")


# ----------------------------user_profile_setemail----------------------------
def test_setemail_successful():
    clear_database()
    user_a = register_n_users(1)
    user_profile_setemail(user_a["token"], "newemail@gmail.com")
    user_a_profile = user_profile(user_a["token"], user_a["u_id"])
    assert user_a_profile["email"] == "newemail@gmail.com"


def test_set_illegal_email():
    clear_database()
    user = register_n_users(1)
    with pytest.raises(InputError):
        user_profile_setemail(user["token"], "invalid_email_address.com")


def test_invalid_token_access():
    clear_database()
    invalid_token = "HAHA"
    with pytest.raises(AccessError):
        user_profile_setemail(invalid_token, "newemail@gmail.com")


# ----------------------------user_profile_sethandle----------------------------
def test_sethandle_successful():
    clear_database()
    user_a = register_n_users(1)

    # Set a new handle name as JOJOKING
    user_profile_sethandle(user_a["token"], "JOJOKING")
    user_a_profile = user_profile(user_a["token"], user_a["u_id"])
    assert user_a_profile["handle_str"] == "JOJOKING"


def test_handle_too_long():
    clear_database()
    user = register_n_users(1)

    # set a long handle name
    with pytest.raises(InputError):
        user_profile_sethandle(user["token"], "Whymynamesolonghahahahhahahaha")


def test_handle_too_short():
    clear_database()
    user = register_n_users(1)

    # set a short handle name
    with pytest.raises(InputError):
        user_profile_sethandle(user["token"], "ha")


def test_handle_duplicate():
    clear_database()
    # return two users with handle name below:
    user_a, user_b = register_n_users(2)

    # Get user_b's profile and we will use his handle as the duplicated handle
    user_b_profile = user_profile(user_b["token"], user_b["u_id"])

    with pytest.raises(InputError):
        user_profile_sethandle(user_a["token"], user_b_profile["handle_str"])


def test_handle_invalid_token():
    clear_database()
    invalid_token = "HAHA"

    with pytest.raises(AccessError):
        user_profile_sethandle(invalid_token, "JOJOJO")
