import pytest
import requests
import json
from test_helpers import url, http_register_n_users
from error import AccessError, InputError


##############################################################
#                   Tests for user/profile                   #
##############################################################


def test_user_profile_successful(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)  # return a user which has profile below:
    #                 email: email0@gmail.com",
    #                 first name: first0
    #                 last name: last0

    # Assert that the returned user profile match what we registered with
    userProfile = requests.get(
        url + "user/profile", params={"token": user["token"], "u_id": user["u_id"]}
    ).json()["user"]
    assert userProfile["email"] == "email0@gmail.com"
    assert userProfile["name_first"] == "first0"
    assert userProfile["name_last"] == "last0"


def test_user_profile_with_invalid_uid(url):
    """
    Testing when there is a user requesting for an user with
    invalid user id.

    We assume it raising InputError
    """
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    # Generate a invalid user id and attempt to retrieve user profile
    invalid_id = -1
    r = requests.get(
        url + "user/profile", params={"token": user["token"], "u_id": invalid_id}
    )
    assert r.status_code == 400


def test_invalid_token_user_profile(url):
    """
    When a user with invalid token request for user profile

    We assume it raising AccessError
    """
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    # Generate an invalid token and attempt to retrieve user profile
    invalid_token = -1
    r = requests.get(
        url + "user/profile", params={"token": invalid_token, "u_id": user["u_id"]}
    )
    assert r.status_code == 403


##############################################################
#               Tests for user/profile/setname               #
##############################################################
def test_setname_successful(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    # set user name to Eric JOJO
    r = requests.put(
        url + "user/profile/setname",
        json={"token": user["token"], "name_first": "Eric", "name_last": "JOJO"},
    )
    assert r.status_code == 200

    # Assert that the name is changed successfully
    userProfile = requests.get(
        url + "user/profile", params={"token": user["token"], "u_id": user["u_id"]}
    ).json()["user"]
    assert userProfile["name_first"] == "Eric"
    assert userProfile["name_last"] == "JOJO"


def test_setname_firstname_empty(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    # set user name to Erichahaha... JOJO
    # first name is too long
    r = requests.put(
        url + "user/profile/setname",
        json={
            "token": user["token"],
            "name_first": "",
            "name_last": "JOJO",
        },
    )
    assert r.status_code == 400


def test_setname_lastname_empty(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    # set user name to Eric JOJOhahaha...
    # last name is too long
    r = requests.put(
        url + "user/profile/setname",
        json={
            "token": user["token"],
            "name_first": "Eric",
            "name_last": "",
        },
    )
    assert r.status_code == 400


def test_setname_firstname_too_long(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    # set user name to Erichahaha... JOJO
    # first name is too long
    r = requests.put(
        url + "user/profile/setname",
        json={
            "token": user["token"],
            "name_first": "Erichaahahahahahahahahahahahahahahahahahahahahahahahahahahahahahaa",
            "name_last": "JOJO",
        },
    )
    assert r.status_code == 400


def test_setname_lastname_too_long(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    # set user name to Eric JOJOhahaha...
    # last name is too long
    r = requests.put(
        url + "user/profile/setname",
        json={
            "token": user["token"],
            "name_first": "Eric",
            "name_last": "JOJOahahahahahahahahahahahahahahahahahahahahahahahahahahahahaa",
        },
    )
    assert r.status_code == 400


def test_setname_invalid_token(url):
    requests.delete(url + "clear")
    # Generate an invalid token
    invalid_token = "HaHa"
    r = requests.put(
        url + "user/profile/setname",
        json={"token": invalid_token, "name_first": "Eric", "name_last": "JOJO"},
    )
    assert r.status_code == 403


##############################################################
#               Tests for user/profile/setemail              #
##############################################################
def test_setemail_successful(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    r = requests.put(
        url + "user/profile/setemail",
        json={"token": user["token"], "email": "newemail@gmail.com"},
    )
    assert r.status_code == 200

    # Assert that email is changed
    userProfile = requests.get(
        url + "user/profile", params={"token": user["token"], "u_id": user["u_id"]}
    ).json()["user"]
    assert userProfile["email"] == "newemail@gmail.com"


def test_set_illegal_email(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    # Attempt to change to a invalid email
    r = requests.put(
        url + "user/profile/setemail",
        json={"token": user["token"], "email": "invalid_email_address.com"},
    )
    assert r.status_code == 400


def test_invalid_token_access(url):
    requests.delete(url + "clear")
    invalid_token = "HAHA"

    # Attempt to change email with an invalid token
    r = requests.put(
        url + "user/profile/setemail",
        json={"token": invalid_token, "email": "newemail@gmail.com"},
    )
    assert r.status_code == 403


##############################################################
#              Tests for user/profile/sethandle              #
##############################################################
def test_sethandle_successful(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    # Set a new handle name as JOJOKING
    r = requests.put(
        url + "user/profile/sethandle",
        json={"token": user["token"], "handle_str": "JOJOKING"},
    )
    assert r.status_code == 200

    userProfile = requests.get(
        url + "user/profile", params={"token": user["token"], "u_id": user["u_id"]}
    ).json()["user"]
    assert userProfile["handle_str"] == "JOJOKING"


def test_handle_too_long(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    # set a long handle name
    r = requests.put(
        url + "user/profile/sethandle",
        json={"token": user["token"], "handle_str": "Whymynamesolonghahahahhahahaha"},
    )
    assert r.status_code == 400


def test_handle_too_short(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    # set a short handle name
    r = requests.put(
        url + "user/profile/sethandle",
        json={"token": user["token"], "handle_str": "ha"},
    )
    assert r.status_code == 400


def test_handle_duplicate(url):
    requests.delete(url + "clear")
    # return two users with handle name below:
    user_a, user_b = http_register_n_users(url, 2)

    # Get user_b's profile and we will use his handle as the duplicated handle
    user_b_profile = requests.get(
        url + "user/profile", params={"token": user_b["token"], "u_id": user_b["u_id"]}
    ).json()["user"]

    r = requests.put(
        url + "user/profile/sethandle",
        json={"token": user_a["token"], "handle_str": user_b_profile["handle_str"]},
    )
    assert r.status_code == 400


def test_handle_invalid_token(url):
    requests.delete(url + "clear")
    invalid_token = "HAHA"

    r = requests.put(
        url + "user/profile/sethandle",
        json={"token": invalid_token, "handle_str": "ha"},
    )
    assert r.status_code == 403


##############################################################
#                      Tests for users/all                   #
##############################################################


def test_users_all_many_users(url):
    requests.delete(url + "clear")

    users = http_register_n_users(url, 3, include_admin=True)

    # Get the three user profile via users/all request
    valid_token = users[1]["token"]
    all_users = requests.get(url + "users/all", params={"token": valid_token}).json()[
        "users"
    ]

    # Get the three user profile one by one via user/profile request
    all_users_info = []
    for user in users:
        profile = requests.get(
            url + "user/profile", params={"token": user["token"], "u_id": user["u_id"]}
        ).json()["user"]
        all_users_info.append(profile)

    # Assert that the info retrieved either way equals
    assert all_users == all_users_info


def test_users_all_invalid_token(url):
    requests.delete(url + "clear")

    # The request should fail as a result of invalid token
    r = requests.get(url + "users/all", params={"token": -1})
    assert r.status_code == 403
