from channel import channel_messages, channel_join
from channels import channels_create
from test_helpers import register_n_users
from message import message_send, message_pin
from other import clear
import pytest
from error import InputError, AccessError
from database import database

INVALID_MESSAGE_ID = -1

def test_message_unpin_public_simple():
    clear()
    user = register_n_users(1)
    # Create a channel and send a message
    channel = channels_create(user["token"], "channel_01", is_public=True)
    message = message_send(user["token"], channel["channel_id"])

    # Return messages in channel
    channel_msg = channel_messages(user["token"], channel["channel_id"], 0)

    # Ensure message is not pinned, then pin message
    assert channel_msg["messages"][0]["is_pinned"] == False
    message_pin(user["token"], message["message_id"])
    assert channel_msg["messages"][0]["is_pinned"] == True

    # Unpin message, ensuring it becomes unpinned
    message_unpin(user["token"], message["message_id"])
    channel_msg = channel_messages(user["token"], channel["channel_id"], 0)
    assert channel_msg["messages"][0]["is_pinned"] == False

def test_message_unpin_private_simple():
    clear()
    user = register_n_users(1)
    # Create a channel and send a message
    channel = channels_create(user["token"], "channel_01", is_public=False)
    message = message_send(user["token"], channel["channel_id"], "test")

    # Return messages in channel
    channel_msg = channel_messages(user["token"], channel["channel_id"], 0)

    # Ensure message is not pinned, then pin message
    assert channel_msg["messages"][0]["is_pinned"] == False
    message_pin(user["token"], message["message_id"])
    assert channel_msg["messages"][0]["is_pinned"] == True

    # Unpin message, ensuring it becomes unpinned
    message_unpin(user["token"], message["message_id"])
    channel_msg = channel_messages(user["token"], channel["channel_id"], 0)
    assert channel_msg["messages"][0]["is_pinned"] == False


def test_message_unpin_invalid_message_id():
    clear()
    user = register_n_users(1)
    # Create a channel and send a message
    channel = channels_create(user["token"], "channel_01", is_public=True)
    message_send(user["token"], channel["channel_id"], "test")

    # Return messages in channel
    channel_msg = channel_messages(user["token"], channel["channel_id"], 0)

    # Ensure message is not pinned, then pin message
    assert channel_msg["messages"][0]["is_pinned"] == False
    message_pin(user["token"], message["message_id"])
    assert channel_msg["messages"][0]["is_pinned"] == True 

    with pytest.raises(InputError):
        message_unpin(user["token"], INVALID_MESSAGE_ID)


# Raise InputError if message already unpinned
def test_message_pin_already_unpinned():
    clear()
    user = register_n_users(1)
    # Create a channel and send a message
    channel = channels_create(user["token"], "channel_01", is_public=True)
    message = message_send(user["token"], channel["channel_id"], "test")

    # Return messages in channel
    channel_msg = channel_messages(user["token"], channel["channel_id"], 0)

    assert channel_msg["messages"][0]["is_pinned"] == False

    # Attempt to unpin a message that is already unpinned
    with pytest.raises(InputError):
        message_unpin(user["token"], message["message_id"])

# Raise error if user is not a member of the channel that
# the message is within
def test_message_unpin_user_not_in_channel():
    clear()
    user_01, user_02 = register_n_users(2)
    # Create a channel and send a message
    channel = channels_create(user_01["token"], "channel_01", is_public=True)
    message = message_send(user_01["token"], channel["channel_id"], "test")

    # Return messages in channel
    channel_msg = channel_messages(user_01["token"], channel["channel_id"], 0)
    assert channel_msg["messages"][0]["is_pinned"] == False
    message_pin(user["token"], message["message_id"])
    assert channel_msg["messages"][0]["is_pinned"] == True 

    # User_02 tries to unpin message 
    with pytest.raises(AccessError):
        message_unpin(user_02["token"], message["message_id"])

# Ensure admin of flockr can unpin any message
def test_message_unpin_flockr_admin_unpin():
    clear()
    admin, user_01, user_02 = register_n_users(3, include_admin=True)
    # Create a channel and send a message
    channel = channels_create(user_01["token"], "channel_01", is_public=True)
    channel_join(user_02["token"], channel["channel_id"])
    message = message_send(user_02["token"], channel["channel_id"], "test")
    # Return messages in channel
    channel_msg = channel_messages(user_01["token"], channel["channel_id"], 0)
    assert channel_msg["messages"][0]["is_pinned"] == False
    
    # Pin message
    message_pin(user_02["token"], message["message_id"])
    assert channel_msg["messages"][0]["is_pinned"] == True 

    # Owner of flockr can unpin any message
    channel_join(admin["token"], channel["channel_id"])
    message_unpin(admin["token"], message["message_id"])
    assert channel_msg["messages"][0]["is_pinned"] == False


# Ensure admin of channel can unpin any message
def test_message_unpin_channel_admin_pin():
    clear()
    user_01, user_02 = register_n_users(2)
    # Create a channel
    channel = channels_create(user_01["token"], "channel_01", is_public=True)

    # User_02 sends a message
    channel_join(user_02["token"], channel["channel_id"])
    message = message_send(user_02["token"], channel["channel_id"], "test")

    # Return messages in channel
    channel_msg = channel_messages(user_01["token"], channel["channel_id"], 0)
    assert channel_msg["messages"][0]["is_pinned"] == False

    # User_02 pins message
    message_pin(user_02["token"], message["message_id"])
    assert channel_msg["messages"][0]["is_pinned"] == True

    # Admin attempts to unpin
    message_unpin(user_01["token"], message["message_id"])
    assert channel_msg["messages"][0]["is_pinned"] == False 



# If any user who tries to pin a message and is part of the
# channel that the message is within but is not an admin,
# an access error will be raised
def test_message_unpin_unauthorised_user():
    clear()
    user_01, user_02 = register_n_users(2)
    # Create a channel and send a message
    channel = channels_create(user_01["token"], "channel_01", is_public=True)
    channel_join(user_01["token"], channel["channel_id"])
    message = message_send(user_01["token"], channel["channel_id"], "test")

    # Return messages in channel
    channel_msg = channel_messages(user_01["token"], channel["channel_id"], 0)
    assert channel_msg["messages"][0]["is_pinned"] == False

    # User_01 pins message
    message_pin(user_01["token"], message["message_id"])

    # Ensure user_02 cannot unpin message
    channel_join(user_02["token"], channel["channel_id"])
    with pytest.raises(AccessError):
        message_unpin(user_02["token"], message["message_id"])


def test_message_unpin_large():
    clear()
    user_01, user_02, user_03, user_04 = register_n_users(4)

    # Create three channels with admins 01, 02, 03 respectively
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

    channel_msg_01 = channel_messages(user_01["token"], channel_01["channel_id"], 0)
    channel_msg_02 = channel_messages(user_02["token"], channel_02["channel_id"], 0)
    channel_msg_03 = channel_messages(user_03["token"], channel_03["channel_id"], 0)

    # Ensure messages are not pinned
    assert channel_msg_01["messages"][0]["is_pinned"] == False
    assert channel_msg_02["messages"][0]["is_pinned"] == False
    assert channel_msg_03["messages"][0]["is_pinned"] == False

    # Owner of each channel pins message sent by user_04
    message_pin(user_01["token"], message_01["message_id"])
    message_pin(user_02["token"], message_02["message_id"])
    message_pin(user_03["token"], message_03["message_id"])

    # Ensure messages are pinned
    assert channel_msg_01["messages"][0]["is_pinned"] == True
    assert channel_msg_02["messages"][0]["is_pinned"] == True
    assert channel_msg_03["messages"][0]["is_pinned"] == True

    # Owner of each channel unpins message sent by user_04
    message_unpin(user_01["token"], message_01["message_id"])
    message_unpin(user_02["token"], message_02["message_id"])
    message_unpin(user_03["token"], message_03["message_id"])

    # Ensure messages are pinned
    assert channel_msg_01["messages"][0]["is_pinned"] == False
    assert channel_msg_02["messages"][0]["is_pinned"] == False
    assert channel_msg_03["messages"][0]["is_pinned"] == False
