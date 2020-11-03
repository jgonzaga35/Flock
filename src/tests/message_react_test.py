import pytest
from message import message_react, message_send
from channels import channels_create
from channel import channel_join
from other import clear
from error import InputError, AccessError
from test_helpers import register_n_users, is_user_reacted


def test_react_succesfully():
    clear()
    user_a, user_b = register_n_users(2)
    public_channel_id = channels_create(user_a["token"], "public_channel", True)[
        "channel_id"
    ]
    # user_b join the channel created by user_a
    channel_join(user_b["token"], public_channel_id)
    message_id = message_send(
        user_a["token"], public_channel_id, "Nice to see you mate"
    )["message_id"]
    message_react(user_b["token"], message_id, 1)
    # User_a and user_b are reacted
    message_react(user_a["token"], message_id, 1)
    assert is_user_reacted(user_b["token"], public_channel_id, message_id, 1)
    assert is_user_reacted(user_a["token"], public_channel_id, message_id, 1)


def test_react_invalid_message_id_in_channel():
    clear()
    user_a, user_b = register_n_users(2)
    # user_a create a channel
    public_channel_id_a = channels_create(user_a["token"], "public_channel_a", True)[
        "channel_id"
    ]
    # user_b create a channel and send message in his own channel
    public_channel_id_b = channels_create(user_b["token"], "public_channel_b", True)[
        "channel_id"
    ]
    message_id_b = message_send(
        user_b["token"], public_channel_id_b, "I am in channel_b"
    )["message_id"]
    # user_a should not be able to react the the message in the public_channel_b
    with pytest.raises(InputError):
        message_react(user_a["token"], message_id_b, 1)


def test_react_invalid_message_id_out_channel():
    clear()
    user_a, user_b = register_n_users(2)
    # user_b create a channel and send message in his own channel
    public_channel_id_b = channels_create(user_b["token"], "public_channel_b", True)[
        "channel_id"
    ]
    message_id_b = message_send(
        user_b["token"], public_channel_id_b, "I am in channel_b"
    )["message_id"]
    # user_a should not be able to react the the message in the public_channel_b
    with pytest.raises(InputError):
        message_react(user_a["token"], message_id_b, 1)


def test_react_invalid_react_id():
    clear()
    user_a = register_n_users(1)
    public_channel_id = channels_create(user_a["token"], "public_channel", True)[
        "channel_id"
    ]
    message_id = message_send(user_a["token"], public_channel_id, "How are you")[
        "message_id"
    ]
    invalid_react_number = -1
    with pytest.raises(InputError):
        message_react(user_a["token"], message_id, invalid_react_number)


def test_react_duplicate_react():
    clear()
    user_a = register_n_users(1)
    public_channel_id = channels_create(user_a["token"], "public_channel", True)[
        "channel_id"
    ]
    message_id = message_send(user_a["token"], public_channel_id, "How are you")[
        "message_id"
    ]
    message_react(user_a["token"], message_id, 1)
    # React to the same message twice
    with pytest.raises(InputError):
        message_react(user_a["token"], message_id, 1)
