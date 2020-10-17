import pytest
import requests
import json
from test_helpers import url
from error import AccessError, InputError

def register_new_account(url):
    return requests.post(
        url + "/auth/register",
        json={
            "email": "email0@gmail.com",
            "password": "passwordthatislongenough0",
            "name_first": "first0",
            "name_last": "last0",
        },
    ).json()

def test_user_profile_successful(url):
    requests.delete(url + "clear")
    user = register_new_account(url)  # return a user which has profile below:
    #                 email: email0@gmail.com",
    #                 first name: first0
    #                 last name: last0

    # We compare the profile above to the returned result.
    userProfile = requests.get(url + "user/profile", params={"token": user["token"], "u_id": user["u_id"]}).json()
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
    user = register_new_account(url)
    # Generate a invalid user id for testing
    invalid_id = -1
    r = requests.get(url + "user/profile", params={"token": user["token"], "u_id": invalid_id})
    assert r.status_code == 400


def test_invalid_token_user_profile(url):
    """
    When a user with invalid token request for user profile

    We assume it raising AccessError
    """
    requests.delete(url + "clear")
    user = register_new_account(url)
    # Generate an invalid token
    invalid_token = "HaHa"
    r = requests.get(url + "user/profile", params={"token": invalid_token, "u_id": user["u_id"]})
    assert r.status_code == 400

# -----------------------------user_profile_setname------------------------------
def test_setname_successful(url):
    requests.delete(url + "clear")
    user = register_new_account(url)
    # set user name to Eric JOJO
    requests.put(url + "user/profile/setname", json={"token": user["token"], "name_first": "Eric", "name_last": "JOJO"})
    userProfile = requests.get(url + "user/profile", params={"token": user["token"], "u_id": user["u_id"]}).json()
    assert userProfile["name_first"] == "Eric"
    assert userProfile["name_last"] == "JOJO"


def test_setname_firstname_too_long(url):
    requests.delete(url + "clear")
    user = register_new_account(url)
    # set user name to Erichahaha... JOJO
    # first name is too long
    r = requests.put(url + "user/profile/setname", json={"token": user["token"], "name_first": "Erichaahahahahahahahahahahahahahahahahahahahahahahahahahahahahahaa", "name_last": "JOJO"})
    assert r.status_code == 400


def test_setname_lastname_too_long(url):
    requests.delete(url + "clear")
    user = register_new_account(url)
    # set user name to Eric JOJOhahaha...
    # last name is too long
    r = requests.put(url + "user/profile/setname", json={"token": user["token"], "name_first": "Eric", "name_last": "JOJOahahahahahahahahahahahahahahahahahahahahahahahahahahahahaa"})
    assert r.status_code == 400  


def test_setname_invalid_token(url):
    requests.delete(url + "clear")
    # Generate an invalid token
    invalid_token = "HaHa"
    r = requests.put(url + "user/profile/setname", json={"token": invalid_token, "name_first": "Eric", "name_last": "JOJO"})
    assert r.status_code == 400  


# ----------------------------user_profile_setemail----------------------------
def test_setemail_successful(url):
    requests.delete(url + "clear")
    user = register_new_account(url)
    requests.put(url + "user/profile/setemail", json={"token": user["token"], "email": "newemail@gmail.com"})
    userProfile = requests.get(url + "user/profile", params={"token": user["token"], "u_id": user["u_id"]}).json()
    assert userProfile["email"] == "newemail@gmail.com"


def test_set_illegal_email(url):
    requests.delete(url + "clear")
    user = register_new_account(url)
    r = requests.put(url + "user/profile/setemail", json={"token": user["token"], "email": "invalid_email_address.com"})
    assert r.status_code == 400  


def test_invalid_token_access(url):
    requests.delete(url + "clear")
    invalid_token = "HAHA"
    r = requests.put(url + "user/profile/setemail", json={"token": invalid_token, "email": "newemail@gmail.com"})
    assert r.status_code == 400  


# ----------------------------user_profile_sethandle----------------------------
def test_sethandle_successful(url):
    requests.delete(url + "clear")
    user = register_new_account(url)

    # Set a new handle name as JOJOKING
    requests.put(url + "user/profile/sethandle", json={"token": user["token"], "handle_str": "JOJOKING"})
    userProfile = requests.get(url + "user/profile", params={"token": user["token"], "u_id": user["u_id"]}).json()
    assert userProfile["handle_str"] == "JOJOKING"


def test_handle_too_long(url):
    requests.delete(url + "clear")
    user = register_new_account(url)

    # set a long handle name
    r = requests.put(url + "user/profile/sethandle", json={"token": user["token"], "handle_str": "Whymynamesolonghahahahhahahaha"})
    assert r.status_code == 400  


def test_handle_too_short(url):
    requests.delete(url + "clear")
    user = register_new_account(url)

    # set a short handle name
    r = requests.put(url + "user/profile/sethandle", json={"token": user["token"], "handle_str": "ha"})
    assert r.status_code == 400  


def test_handle_duplicate(url):
    requests.delete(url + "clear")
    # return two users with handle name below:
    user_a = register_new_account(url)
    user_b = requests.post(
        url + "/auth/register",
        json={
            "email": "email1@gmail.com",
            "password": "passwordthatislongenough1",
            "name_first": "first1",
            "name_last": "last1",
        },
    ).json()

    # Get user_b's profile and we will use his handle as the duplicated handle
    user_b_profile = requests.get(url + "user/profile", params={"token": user_b["token"], "u_id": user_b["u_id"]}).json()

    r = requests.put(url + "user/profile/sethandle", json={"token": user_a["token"], "handle_str": user_b_profile["handle_str"]})
    assert r.status_code == 400  


def test_handle_invalid_token(url):
    requests.delete(url + "clear")
    invalid_token = "HAHA"

    r = requests.put(url + "user/profile/sethandle", json={"token": invalid_token, "handle_str": "ha"})
    assert r.status_code == 400
