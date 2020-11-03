from channel import channel_messages, channel_join
from message import message_send
from channels import channels_create, channels_list
from other import clear
from error import InputError, AccessError
from word_list import word_list
import time
import random
import pytest
from test_helpers import register_n_users

#################################################################################
#                       Tests for channel_messages
#################################################################################
def test_messages_no_messages():
    clear()
    user = register_n_users(1)
    channel = channels_create(user["token"], "channel", is_public=True)
    messages_in_channel = channel_messages(
        user["token"], channel["channel_id"], start=0
    )

    assert len(messages_in_channel["messages"]) == 0
    assert messages_in_channel["start"] == 0
    assert messages_in_channel["end"] == -1


def test_messages_invalid_channel_ID():
    clear()
    user = register_n_users(1)
    invalid_channel_id = -1
    with pytest.raises(InputError):
        assert channel_messages(user["token"], invalid_channel_id, 0)


def test_channel_messages_invalid_start():
    clear()
    user = register_n_users(1)

    channel_id = channels_create(user["token"], "channel", is_public=True)["channel_id"]

    with pytest.raises(InputError):
        assert channel_messages(user["token"], channel_id, start=-1)

    with pytest.raises(InputError):
        assert channel_messages(user["token"], channel_id, start=1)


def test_messages_user_not_member():
    clear()

    user_01, user_02 = register_n_users(2)
    channel = channels_create(user_01["token"], "channel_01", is_public=True)
    channel_join(user_01["token"], channel["channel_id"])

    with pytest.raises(AccessError):
        assert channel_messages(user_02["token"], channel["channel_id"], 0)


def test_messages_invalid_token():
    clear()
    with pytest.raises(AccessError):
        channel_messages(-1, 0, 0)


def test_messages_negative_start_index():
    clear()
    # Add a user and log them in
    user = register_n_users(1)

    # Create a channel and fill with messages
    channel = channels_create(user["token"], "new_channel", is_public=True)
    populate_channel_hundred_messages(user["token"], channel["channel_id"])
    with pytest.raises(InputError):
        assert channel_messages(user["token"], channel["channel_id"], -1)


def test_messages_simple():
    clear()
    # Add a user and log them in
    user = register_n_users(1)

    # Create a channel and fill with messages
    channel = channels_create(user["token"], "new_channel", is_public=True)
    message_send(user["token"], channel["channel_id"], "Hello World!")
    res = channel_messages(user["token"], channel["channel_id"], 0)
    assert res["messages"][0]["message"] == "Hello World!"


def test_messages_start_overflow():
    clear()
    user = register_n_users(1)
    channel = channels_create(user["token"], "channel_01", is_public=True)
    channel_join(user["token"], channel["channel_id"])
    message_send(user["token"], channel["channel_id"], "Hello World!")
    with pytest.raises(InputError):
        assert channel_messages(user["token"], channel["channel_id"], 100)


def test_messages_start_underflow():
    clear()
    user = register_n_users(1)

    channel = channels_create(user["token"], "channel_01", is_public=True)
    channel_join(user["token"], channel["channel_id"])
    message_send(user["token"], channel["channel_id"], "Hello World!")
    assert channel_messages(user["token"], channel["channel_id"], 0)["end"] == -1


def test_channel_message_a_lot_of_message():
    """
    This test uses randomness. That means that running this test twice will
    not do the exact same thing, so sometimes it might fail, sometimes not.

    If it does, then pytest will print out the seed. Copy it, and then give it
    to random.seed (below). Like this, the random module will always generate
    the same sequence of random number, and you can debug the failing test case.
    """
    seed = time.time()
    print("seed", seed)
    random.seed(seed)

    clear()
    usera, userb, userc = register_n_users(3)
    channel_id = channels_create(usera["token"], "channel", is_public=True)[
        "channel_id"
    ]

    channel_join(userb["token"], channel_id)
    channel_join(userc["token"], channel_id)

    # generate random messages
    for _ in range(340):
        token = random.choice([usera, userb, userc])["token"]
        word = random.choice(word_list)
        message_send(token, channel_id, word)

    # make sure that usera, userb and userc all get the same messages
    assert channel_messages(userb["token"], channel_id, 5) == channel_messages(
        userc["token"], channel_id, 5
    )
    assert channel_messages(userb["token"], channel_id, 5) == channel_messages(
        usera["token"], channel_id, 5
    )

    # makes sure all of the message are sorted by date (newer first)
    #    messages[0] should be newer than messages[1]
    #    => messages[0]['time_created'] > messages[1]['time_created']
    messages = channel_messages(userc["token"], channel_id, random.randint(0, 340))[
        "messages"
    ]
    prev_msg_time = None
    for message in messages:
        if prev_msg_time is None:
            prev_msg_time = message["time_created"]
        else:
            assert prev_msg_time >= message["time_created"]
            prev_msg_time = message["time_created"]

    # makes sure that start and end make sense when we can load 50 messages
    assert channel_messages(userb["token"], channel_id, 5)["start"] == 5
    assert channel_messages(userb["token"], channel_id, 5)["end"] == 55

    # make sure that start and end make sense when we can't load 50 messages
    assert channel_messages(userb["token"], channel_id, 330)["start"] == 330
    assert channel_messages(userb["token"], channel_id, 330)["end"] == -1


# Helper function to send 100 messages to a given channel
def populate_channel_hundred_messages(token, channel_id):
    for _ in range(1, 100):
        index = random.randint(0, len(word_list) - 1)
        message = word_list[index]
        message_send(token, channel_id, message)
