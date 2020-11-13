import time
import pytest
from channels import channels_create
from channel import channel_messages, channel_join
from message import sendlater
from other import clear
from error import InputError, AccessError
from test_helpers import register_n_users

# bump this up if you are running on a potato computer. It will scale delays,
# but tests will *take* longer (not *run* slower)
DELAY_SCALE = 1  # it should be an integer

ERR_TOO_SLOW = "potato computer detected. Bump up DELAY_SCALE, or try to re-run"


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


def test_sendlater_single():
    clear()
    # setup
    user = register_n_users(1)
    channel_id = channels_create(user["token"], "name", is_public=True)["channel_id"]

    # send message with delay
    send_at = int(round(time.time() + 1 * DELAY_SCALE))
    sendlater(user["token"], channel_id, "message", send_at)

    # make sure there are now messages
    messages = channel_messages(user["token"], channel_id, start=0)
    assert int(round(time.time())) < send_at, ERR_TOO_SLOW
    assert len(messages["messages"]) == 0

    # wait for the message to be sent
    time.sleep(2)

    # check that the message is there
    messages = channel_messages(user["token"], channel_id, start=0)
    assert len(messages["messages"]) == 1
    assert messages["messages"][0]["message"] == "message"

    # if this fails, there has been a time difference of more than half a second
    # time.time() is a float, and floats shouldn't be compared with ==
    assert messages["messages"][0]["time_created"] - send_at <= 1


def test_sendlater_backwards():
    """send two messages with delay, where the first one has a longer delay
    than the second. Hence the backwards"""
    clear()
    # setup
    usera, userb = register_n_users(2)
    channel_id = channels_create(usera["token"], "name", is_public=True)["channel_id"]
    channel_join(userb["token"], channel_id)

    send_at_a = int(round(time.time() + 3 * DELAY_SCALE))
    # message b will be sent *before* message a
    send_at_b = int(round(time.time() + 1 * DELAY_SCALE))

    sendlater(usera["token"], channel_id, "message a", send_at_a)
    sendlater(userb["token"], channel_id, "message b", send_at_b)

    messages = channel_messages(usera["token"], channel_id, start=0)
    assert int(round(time.time())) < send_at_b, ERR_TOO_SLOW
    assert len(messages["messages"]) == 0

    # wait for the first message (message B) to be sent
    time.sleep(2)

    messages = channel_messages(usera["token"], channel_id, start=0)
    assert int(round(time.time())) < send_at_a, ERR_TOO_SLOW
    assert len(messages["messages"]) == 1
    assert messages["messages"][0]["message"] == "message b"
    assert (messages["messages"][0]["time_created"] - send_at_b) <= 1

    # wait for the second message (message A) to be sent
    time.sleep(2)

    messages = channel_messages(userb["token"], channel_id, start=0)
    assert len(messages["messages"]) == 2
    assert messages["messages"][0]["message"] == "message a"
    assert (messages["messages"][0]["time_created"] - send_at_a) <= 1
