import pytest
from werkzeug.wrappers import UserAgentMixin
from message import message_react, message_send, message_unreact
from channels import channels_create
from channel import channel_join, channel_leave, channel_messages
from other import clear
from error import InputError
from test_helpers import register_n_users


def test_messages_unreact_successfully():
    clear()
    user_a, user_b = register_n_users(2)
    # user_a create a public channel
    channel_a_id = channels_create(user_a["token"], "channel_a", True)["channel_id"]
    channel_join(user_b["token"], channel_a_id)
    message_id = message_send(user_b["token"], channel_a_id, "Hi, user_a")["message_id"]
    message_react(user_a["token"], message_id, 1)
    # User_a has reacted to the channel
    message = channel_messages(user_a["token"], channel_a_id, 0)["messages"][0]
    assert message["reacts"][0]["is_this_user_reacted"] == True
    # User_a has unreacted to the channel
    message_unreact(user_a["token"], message_id, 1)
    message = channel_messages(user_a["token"], channel_a_id, 0)["messages"][0]
    assert message["reacts"][0]["is_this_user_reacted"] == False


def test_unreact_invalid_message_id_out_channel():
    """
    Test a situation where a user trying to unreact to a message
    but not in that channel
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
    # user_a join the channel and react to the user_b
    channel_join(user_a["token"], public_channel_id_b)
    message_react(user_a["token"], message_id_b, 1)
    # user_a leave the channel
    channel_leave(user_a["token"], public_channel_id_b)
    # user_a should not be able to react the the message in the public_channel_b
    with pytest.raises(InputError):
        message_unreact(user_a["token"], message_id_b, 1)


def test_unreact_invalid_message_id():
    """
    Test user trying to unreact to a invalid message id
    """
    clear()
    user_a = register_n_users(1)
    invalid_message_id = -1
    with pytest.raises(InputError):
        message_unreact(user_a["token"], invalid_message_id, 1)


def test_unreact_invalid_react_id():
    clear()
    user_a = register_n_users(1)
    public_channel_id = channels_create(user_a["token"], "public_channel", True)[
        "channel_id"
    ]
    message_id = message_send(user_a["token"], public_channel_id, "How are you")[
        "message_id"
    ]
    message_react(user_a["token"], message_id, 1)
    invalid_react_number = -1
    with pytest.raises(InputError):
        message_unreact(user_a["token"], message_id, invalid_react_number)


def test_unreact_inactive_react_id():
    clear()
    user_a = register_n_users(1)
    public_channel_id = channels_create(user_a["token"], "public_channel", True)[
        "channel_id"
    ]
    message_id = message_send(user_a["token"], public_channel_id, "How are you")[
        "message_id"
    ]
    # React id 1 is a valid id but not active
    with pytest.raises(InputError):
        message_unreact(user_a["token"], message_id, 1)


def test_unreact_curren_user_not_react():
    """
    This is to test the situation where the user is not reacted to a existing message,
    but other user has reacted to the message
    """
    clear()
    user_a, user_b = register_n_users(2)
    channel_a_id = channels_create(user_a["token"], "channel_a", True)["channel_id"]
    channel_join(user_b["token"], channel_a_id)
    message_id = message_send(user_a["token"], channel_a_id, "Hi, user_b")["message_id"]
    message_react(user_b["token"], message_id, 1)
    # user_a react to a message that he hasn't reacted
    with pytest.raises(InputError):
        message_unreact(user_a["token"], message_id, 1)
