import time
import pytest
from channels import channels_create
from message import sendlater
from other import clear
from error import InputError, AccessError
from test_helpers import register_n_users


def test_sendlater_invalid_token():
    clear()
    user = register_n_users(1)
    channel_id = channels_create(user["token"], "name", is_public=True)["channel_id"]
    with pytest.raises(AccessError):
        sendlater(-1, channel_id, "message", time.time() + 2)


def test_sendlater_invalid_channel():
    clear()
    user = register_n_users(1)
    with pytest.raises(InputError):
        sendlater(user["token"], -1, "message", time.time() + 2)


def test_sendlater_invalid_message():
    clear()
    user = register_n_users(1)
    channel_id = channels_create(user["token"], "name", is_public=True)["channel_id"]
    sendlater(user["token"], channel_id, "m" * 1000, time.time() + 2)

    with pytest.raises(InputError):
        sendlater(user["token"], channel_id, "m" * 1001, time.time() + 2)


def test_sendlater_invalid_time():
    clear()
    user = register_n_users(1)
    channel_id = channels_create(user["token"], "name", is_public=True)["channel_id"]
    with pytest.raises(InputError):
        sendlater(user["token"], channel_id, "message", time.time() - 1)
