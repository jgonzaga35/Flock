import pytest
import requests
import json
from test_helpers import url
from error import AccessError, InputError

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
    return requests.post(
        url + "/channels/create",
        json={
            "token": "validemail@gmail.com",
            "name": "123abc!@#",
            "is_public": "Hayden,
        },
    ).json()
