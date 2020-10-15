from message import message_remove, message_send
from channel import channel_messages, channel_join
from channels import channels_create, channels_list
from test_helpers import register_n_users
from database import database, clear_database

import pytest
from error import AccessError, InputError

INVALID_USER_TOKEN = -1
INVALID_MESSAGE_ID = -1
#######################################################
#               Tests for message_remove              #
#######################################################
def test_remove_invalid_user_token():
    clear_database()
    user = register_n_users(1)

    # Create a new channel
    channel = channels_create(user["token"], "channel01", is_public=True)
    # User sends a message
    message = message_send(user["token"], channel["channel_id"], "test message")
    # Non-existent user tries to remove the message
    with pytest.raises(AccessError):
        assert message_remove(INVALID_USER_TOKEN, message["message_id"])


def test_remove_invalid_message_id():
    clear_database()
    user = register_n_users(1)

    # Create a new channel
    channel = channels_create(user["token"], "channel01", is_public=True)
    # User sends a message
    message_send(user["token"], channel["channel_id"], "test message")
    # User tries to remove message with an invalid message id (doesn't exist)
    with pytest.raises(InputError):
        assert message_remove(user["token"], INVALID_MESSAGE_ID)


# User tries to remove a message that they are not authorised to remove
def test_remove_unauthorised_user():
    clear_database()
    user01, user02 = register_n_users(2)

    # Create channel with message from user01
    channel = channels_create(user01["token"], "channel", is_public=True)
    message = message_send(user01["token"], channel["channel_id"], "test message")
    # User02 tries to remove message from user01
    with pytest.raises(AccessError):
        message_remove(user02["token"], message["message_id"])


# Test that the owner of the channel can remove any message
def test_remove_owner_permissions():
    clear_database()
    user01, user02 = register_n_users(2)

    # Create a new channel with user01 as admin
    channel = channels_create(user01["token"], "channel", is_public=True)
    channel_join(user02["token"], channel["channel_id"])

    message = message_send(user02["token"], channel["channel_id"], "test message")
    message_remove(user01["token"], message["message_id"])
    assert message["message_id"] not in [
        x["message_id"]
        for x in database["channels"][channel["channel_id"]]["messages"].values()
    ]


def test_remove_message_non_existent():
    clear_database()
    user = register_n_users(1)
    channel = channels_create(user["token"], "channel", is_public=True)
    message = message_send(user["token"], channel["channel_id"], "test message")
    message_remove(user["token"], message["message_id"])

    with pytest.raises(InputError):
        message_remove(user["token"], message["message_id"])


# Every message has a unique ID - including messages that are deleted
# i.e. active messages and deleted messages cannot have the same ID
# This allows for blackbox testing
