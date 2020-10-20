import pytest
import requests
import json
from test_helpers import url, http_register_n_users
from error import AccessError, InputError


def test_user_profile_successful(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)  # return a user which has profile below:
    #                 email: email0@gmail.com",
    #                 first name: first0
    #                 last name: last0

    # We compare the profile above to the returned result.
    userProfile = requests.get(
        url + "user/profile", params={"token": user["token"], "u_id": user["u_id"]}
    ).json()["user"]
    print(userProfile)
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
    # Generate a invalid user id for testing
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
    # Generate an invalid token
    invalid_token = -1
    r = requests.get(
        url + "user/profile", params={"token": invalid_token, "u_id": user["u_id"]}
    )
    print(r)
    assert r.status_code == 403


# -----------------------------user_profile_setname------------------------------
def test_setname_successful(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    # set user name to Eric JOJO
    requests.put(
        url + "user/profile/setname",
        json={"token": user["token"], "name_first": "Eric", "name_last": "JOJO"},
    )
    userProfile = requests.get(
        url + "user/profile", params={"token": user["token"], "u_id": user["u_id"]}
    ).json()["user"]
    assert userProfile["name_first"] == "Eric"
    assert userProfile["name_last"] == "JOJO"


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


# ----------------------------user_profile_setemail----------------------------
def test_setemail_successful(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    requests.put(
        url + "user/profile/setemail",
        json={"token": user["token"], "email": "newemail@gmail.com"},
    )
    userProfile = requests.get(
        url + "user/profile", params={"token": user["token"], "u_id": user["u_id"]}
    ).json()["user"]
    assert userProfile["email"] == "newemail@gmail.com"


def test_set_illegal_email(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    r = requests.put(
        url + "user/profile/setemail",
        json={"token": user["token"], "email": "invalid_email_address.com"},
    )
    assert r.status_code == 400


def test_invalid_token_access(url):
    requests.delete(url + "clear")
    invalid_token = "HAHA"
    r = requests.put(
        url + "user/profile/setemail",
        json={"token": invalid_token, "email": "newemail@gmail.com"},
    )
    assert r.status_code == 403


# ----------------------------user_profile_sethandle----------------------------
def test_sethandle_successful(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    # Set a new handle name as JOJOKING
    requests.put(
        url + "user/profile/sethandle",
        json={"token": user["token"], "handle_str": "JOJOKING"},
    )
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


def test_users_all_many_users(url):
    requests.delete(url + "clear")

    users = http_register_n_users(url, 3)

    valid_token = users[1]["token"]
    all_users = requests.get(url + "users/all", params={"token": valid_token}).json()
    print(all_users)

    all_users_info = []
    for user in users:
        profile = requests.get(
            url + "user/profile", params={"token": user["token"], "u_id": user["u_id"]}
        ).json()["user"]
        all_users_info.append(profile)

    assert all_users == all_users_info


def test_users_all_invalid_token(url):
    requests.delete(url + "clear")

    r = requests.get(url + "users/all", params={"token": -1})
    assert r.status_code == 403
