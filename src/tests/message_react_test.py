import pytest
from message import message_react, message_send
from channels import channels_create
from channel import channel_join, channel_messages
from other import clear
from error import InputError
from test_helpers import register_n_users


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

    # user_a react to his own message
    message_react(user_a["token"], message_id, 1)

    # Message from the perspective of user_a
    message_a = channel_messages(user_a["token"], public_channel_id, 0)["messages"][0]
    # user_a reacted
    assert message_a["reacts"][0]["is_this_user_reacted"] == True
    assert user_a["u_id"] in message_a["reacts"][0]["u_ids"]

    # Message from the perspective of user_b
    message_b = channel_messages(user_b["token"], public_channel_id, 0)["messages"][0]
    # user_b haven't reacted
    assert message_b["reacts"][0]["is_this_user_reacted"] == False
    # user_b react to the message
    message_react(user_b["token"], message_id, 1)
    message_b = channel_messages(user_b["token"], public_channel_id, 0)["messages"][0]
    assert message_b["reacts"][0]["is_this_user_reacted"] == True
    assert user_b["u_id"] in message_b["reacts"][0]["u_ids"]


def test_react_invalid_message_id_in_different_channel():
    """
    Test the situation where the user trying to react to a message but
    not in that channel
    """
    clear()
    user_a, user_b = register_n_users(2)
    # user_a create a channel
    channels_create(user_a["token"], "public_channel_a", True)["channel_id"]
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


def test_react_invalid_message_id_in_channel():
    """
    Test user trying to unreact to a invalid message id
    """
    clear()
    user_a = register_n_users(1)
    channels_create(user_a["token"], "channel_a", True)
    invalid_channel_id = -1
    with pytest.raises(InputError):
        message_react(user_a["token"], invalid_channel_id, 1)


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
