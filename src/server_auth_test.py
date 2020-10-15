import pytest
import requests
import json
from test_helpers import url
from error import AccessError, InputError

VALID_LOGIN_INFO = {"email": "validemail@gmail.com", "password": "123abc!@#"}


def register_new_account(url):
    return requests.post(
        url + "auth/register",
        json={
            "email": "validemail@gmail.com",
            "password": "123abc!@#",
            "name_first": "Hayden",
            "name_last": "Everest"
        }
    ).json()


def test_login_success_case(url):
    requests.delete(url + "clear")
    user1 = register_new_account()
    # when we register a new account, the user is logged in
    assert (
        requests.post(url + "auth/logout", json={"token":user1["token"]}).json()["is_success"]
        == True
    )
    assert (
        requests.post(url + "auth/login", json=VALID_LOGIN_INFO).json()["u_id"]
        == user1["u_id"]
    )


def test_login_double_login(url):
    requests.delete(url + "clear")
    register_new_account()
    # when we register a new account, the user is logged in
    token1 = requests.post(url + "auth/login", json=VALID_LOGIN_INFO).json()["token"]
    token2 = requests.post(url + "auth/login", json=VALID_LOGIN_INFO).json()["token"]
    assert token1 == token2
    assert (
        requests.post(url + "auth/logout", json={"token": token1}).json()["is_success"] == True
    )
    # A user shouldn't be logout twice just because they log in twice
    assert (
        requests.post(url + "auth/logout", json={"token": token2}).json()["is_success"] == False
    )


def test_login_invalid_email(url):
    requests.delete(url + "clear")
    with pytest.raises(InputError):
        requests.post(url + "auth/login", json={"email": "didntusethis@gmail", "password": "123abcd!@#"})
    with pytest.raises(InputError):
        requests.post(url + "auth/login", json={"email": "didntusethis.com", "password": "123abcd!@#"})


def test_login_wrong_password(url):
    requests.delete(url + "clear")
    register_new_account()
    with pytest.raises(InputError):
        requests.post(url + "auth/login", json={"email": "validemail@gmail.com", "password": "123"})


def test_login_never_registered(url):
    requests.delete(url + "clear")
    with pytest.raises(InputError):
        requests.post(url + "auth/login", json={"email": "didntusethis@gmail.com", "password": "123abcd!@#"})
