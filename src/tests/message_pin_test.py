from test_helpers import register_n_users
from channels import channels_create, channel_messages
from message import message_send, message_pin
import pytest
from error import InputError, AccessError

INVALID_MESSAGE_ID - 1


def test_message_pin_public_simple():
    user = register_n_users(1)
    # Create a channel and send a message
    channel = channels_create(user["token"], "channel_01", is_public=True)
    message = message_send(user["token"], channel["channel_id"], "test")

    # Return messages in channel
    channel_msg = channel_messages(user["token"], channel["channel_id"], 0)

    # Ensure message is not pinned
    assert channel_msg["messages"]["is_pinned"] == False
    message_pin(user["token"], message["message_id"])
    assert channel_msg["messages"]["is_pinned"] == True


def test_message_pin_private_simple():
    user = register_n_users(1)
    # Create a channel and send a message
    channel = channels_create(user["token"], "channel_01", is_public=False)
    message = message_send(user["token"], channel["channel_id"], "test")

    # Return messages in channel
    channel_msg = channel_messages(user["token"], channel["channel_id"], 0)

    # Ensure message is not pinned
    assert channel_msg["messages"]["is_pinned"] == False
    message_pin(user["token"], message["message_id"])
    assert channel_msg["messages"]["is_pinned"] == True


def test_message_pin_invalid_message_id():
    user = register_n_users(1)
    # Create a channel and send a message
    channel = channels_create(user["token"], "channel_01", is_public=True)
    message = message_send(user["token"], channel["channel_id"], "test")

    # Return messages in channel
    channel_msg = channel_messages(user["token"], channel["channel_id"], 0)

    # Ensure message is not pinned
    assert channel_msg["messages"]["is_pinned"] == False

    with pytest.raises(InputError):
        message_pin(user["token"], INVALID_MESSAGE_ID)


# Raise InputError if message already pinned
def test_message_pin_already_pinned():
    user = register_n_users(1)
    # Create a channel and send a message
    channel = channels_create(user["token"], "channel_01", is_public=True)
    message = message_send(user["token"], channel["channel_id"], "test")

    # Return messages in channel
    channel_msg = channel_messages(user["token"], channel["channel_id"], 0)

    assert channel_msg["messages"]["is_pinned"] == False
    message_pin(user["token"], message["message_id"])

    # Attempt to pin a message that is already pinned
    with pytest.rasies(InputError):
        message_pin(user["token"], message["message_id"])


# Raise error if user is not a member of the channel that
# the message is within
def test_message_pin_user_not_in_channel():
    user_01, user_02 = register_n_users(2)
    # Create a channel and send a message
    channel = channels_create(user_01["token"], "channel_01", is_public=True)
    message = message_send(user_01["token"], channel["channel_id"], "test")

    # Return messages in channel
    channel_msg = channel_messages(user_01["token"], channel["channel_id"], 0)
    assert channel_msg["messages"]["is_pinned"] == False

    # User_02 tries to pin channel
    with pytest.raises(AccessError):
        message_pin(user_02["token"], message["message_id"])


# Ensure owner of flockr can pin any message
def test_message_pin_flockr_owner_pin():
    owner, user_01, user_02 = register_n_users(2)
    # Create a channel and send a message
    channel = channels_create(user_01["token"], "channel_01", is_public=True)
    channel_join(user_02["token"], channel["channel_id"])
    message = message_send(user_02["token"], channel["channel_id"], "test")

    # Return messages in channel
    channel_msg = channel_messages(user_01["token"], channel["channel_id"], 0)
    assert channel_msg["messages"]["is_pinned"] == False

    # Owner of flockr can pin any message
    channel_join(owner["token"], channel["channel_id"])
    message_pin(owner["token"], message["message_id"])
    assert channel_msg["messages"]["is_pinned"] == True


# Ensure owner of channel can pin any message
def test_message_pin_channel_owner_pin():
    owner, user_01, user_02 = register_n_users(2)
    # Create a channel
    channel = channels_create(user_01["token"], "channel_01", is_public=True)

    # User_02 sends a message
    channel_join(user_02["token"], channel["channel_id"])
    message = message_send(user_02["token"], channel["channel_id"], "test")

    # Return messages in channel
    channel_msg = channel_messages(user_01["token"], channel["channel_id"], 0)
    assert channel_msg["messages"]["is_pinned"] == False

    # Owner of channel attempts to pin message
    message_pin(user_01["token"], message["message_id"])
    assert channel_msg["messages"]["is_pinned"] == True


# If any user who tries to pin a message and is part of the
# channel that the message is within but is not an owner,
# an access error will be raised
def test_message_pin_unauthorised_user():
    owner, user_01, user_02 = register_n_users(2)
    # Create a channel and send a message
    channel = channels_create(user_01["token"], "channel_01", is_public=True)
    channel_join(user_02["token"], channel["channel_id"])
    message = message_send(user_02["token"], channel["channel_id"], "test")

    # Return messages in channel
    channel_msg = channel_messages(user_01["token"], channel["channel_id"], 0)
    assert channel_msg["messages"]["is_pinned"] == False

    # Ensure user_02 cannot pin message
    message_pin(user_02["token"], message["message_id"])
    assert channel_msg["messages"]["is_pinned"] == True


def test_message_pin_large():
    owner, user_01, user_02, user_03, user_04 = register_n_users(5)

    # Create three channels with owners 01, 02, 03 respectively
    channel_01 = channels_create(user_01["token"], "channel_01", is_public=True)
    channel_02 = channels_create(user_02["token"], "channel_01", is_public=True)
    channel_03 = channels_create(user_03["token"], "channel_01", is_public=True)

    # User_04 joins each channel
    channel_join(user_04["token"], channel_01["channel_id"])
    channel_join(user_04["token"], channel_02["channel_id"])
    channel_join(user_04["token"], channel_03["channel_id"])

    # User_04 sends a message in each channel
    message_01 = message_send(user_04["token"], channel_01["channel_id"], "01")
    message_02 = message_send(user_04["token"], channel_02["channel_id"], "02")
    message_03 = message_send(user_04["token"], channel_03["channel_id"], "03")

    # Ensure messages are not pinned
    assert channel_msg["messages"]["is_pinned"] == False
    assert channel_msg["messages"]["is_pinned"] == False
    assert channel_msg["messages"]["is_pinned"] == False

    # Owner of each channel pins message sent by use_04
    message_pin(user_01["token"], message_01["message_id"])
    message_pin(user_02["token"], message_02["message_id"])
    message_pin(user_03["token"], message_03["message_id"])

    # Ensure messages are pinned
    assert channel_msg["messages"]["is_pinned"] == True
    assert channel_msg["messages"]["is_pinned"] == True
    assert channel_msg["messages"]["is_pinned"] == True
