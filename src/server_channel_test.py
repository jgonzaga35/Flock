import pytest
import requests
import json
from test_helpers import url
from error import AccessError, InputError

VALID_LOGIN_INFO = {"email": "validemail@gmail.com", "password": "123abc!@#"}

def register_new_account(url):
    return requests.post(
        url + "/auth/register",
        json={
            "email": "validemail@gmail.com",
            "password": "123abc!@#",
            "name_first": "Hayden",
            "name_last": "Everest",
        },
    ).json()

def create_new_channel(url):

    token = auth_login("validemail@gmail.com", "123abc!@#")["token"]
    return requests.post(
        url + "/channels/create",
        json={
            "token": token,
            "name": "Hayden",
            "is_public": True,
        },
    ).json()

def test_channel_join_success(url):
    requests.delete(url + "clear")
    user = register_new_account(url)
    token = requests.post(url + "auth/login", json=VALID_LOGIN_INFO).json()["token"]
    assert (
        requests.post(url + "channel_create", json=)


    )
    token = 

    assert register_new_account(url)['code'] == 404
