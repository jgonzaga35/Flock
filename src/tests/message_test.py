from message import message_send, message_remove, message_edit
from auth import auth_register
from channel import (
    channel_join,
    channel_details,
    channel_messages,
    channel_addowner,
    channel_invite,
    channel_leave,
)
from channels import channels_create, channels_list
from test_helpers import register_n_users, assert_contains_users_id
from database import database
from other import clear

import time
import pytest
from error import AccessError, InputError

INVALID_USER_TOKEN = -1
INVALID_MESSAGE_ID = -1

##################################################################################
#                           Tests for message_remove                             #
##################################################################################
def test_remove_invalid_user_token():
    clear()
    user = register_n_users(1)

    # Create a new channel
    channel = channels_create(user["token"], "channel01", is_public=True)
    # User sends a message
    message = message_send(user["token"], channel["channel_id"], "test message")
    # Non-existent user tries to remove the message
    with pytest.raises(AccessError):
        assert message_remove(INVALID_USER_TOKEN, message["message_id"])


def test_remove_invalid_message_id():
    clear()
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
    clear()
    user01, user02 = register_n_users(2)

    # Create channel with message from user01
    channel = channels_create(user01["token"], "channel", is_public=True)
    channel_join(user02["token"], channel["channel_id"])
    message = message_send(user01["token"], channel["channel_id"], "test message")
    # User02 tries to remove message from user01
    with pytest.raises(AccessError):
        message_remove(user02["token"], message["message_id"])


# Test that the owner of the flockr can remove any message
def test_remove_owner_flock_permissions():
    clear()
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


# Test that the owner of a channel can remove any message
def test_remove_owner_channel_permissions():
    clear()
    user01, user02, user03 = register_n_users(3)

    channels_create(user01["token"], "channel01", is_public=True)
    channel02 = channels_create(user02["token"], "channel02", is_public=True)
    channel_join(user03["token"], channel02["channel_id"])

    message = message_send(user03["token"], channel02["channel_id"], "test message")
    message_remove(user02["token"], message["message_id"])

    assert message["message_id"] not in [
        x["message_id"]
        for x in database["channels"][channel02["channel_id"]]["messages"].values()
    ]


# Sending an empty messsage - waiting until this is clarified
# def test_remove_send_empty_message():
#     clear()
#     user = register_n_users(1)

#     channel = channels_create(user["token"], "channel", is_public=True)
#     message = message_send(user["token"], channel["channel_id"], "")
#     with pytest.raises(AccessError):
#         message_remove(user["token"], message["message_id"])


def test_remove_message_non_existent():
    clear()
    user = register_n_users(1)
    channel = channels_create(user["token"], "channel", is_public=True)
    message = message_send(user["token"], channel["channel_id"], "test message")
    message_remove(user["token"], message["message_id"])

    with pytest.raises(InputError):
        message_remove(user["token"], message["message_id"])


def test_remove_continuous_send():
    clear()
    user = register_n_users(1)
    channel_id = channels_create(user["token"], "channela", is_public=True)[
        "channel_id"
    ]

    for i in range(1, 50):
        message = message_send(user["token"], channel_id, "message " + str(i))
        message_remove(user["token"], message["message_id"])

    assert channel_messages(user["token"], channel_id, 0)["end"] == -1
    assert bool(channel_messages(user["token"], channel_id, 0)["messages"]) == False


# Implement a large flockr to test messages are removed correctly
def test_remove_multiple_channels():
    clear()
    user01, user02, user03 = register_n_users(3)

    # User01 owner of all three channels, user02 and user 03 members
    channel_id_01 = channels_create(user01["token"], "channela", is_public=True)[
        "channel_id"
    ]
    channel_join(user02["token"], channel_id_01)
    channel_join(user03["token"], channel_id_01)
    channel_id_02 = channels_create(user01["token"], "channela", is_public=True)[
        "channel_id"
    ]
    channel_join(user02["token"], channel_id_02)
    channel_join(user03["token"], channel_id_02)
    channel_id_03 = channels_create(user01["token"], "channela", is_public=True)[
        "channel_id"
    ]
    channel_join(user02["token"], channel_id_03)
    channel_join(user03["token"], channel_id_03)

    # message_#_id_[user who sent message]
    message_1_id_user02 = message_send(
        user02["token"], channel_id_01, "message 1 by user 2"
    )
    message_2_id_user02 = message_send(
        user02["token"], channel_id_02, "message 2 by user 2"
    )
    message_3_id_user02 = message_send(
        user02["token"], channel_id_03, "message 3 by user 2"
    )
    message_1_id_user03 = message_send(
        user03["token"], channel_id_01, "message 1 by user 3"
    )
    message_2_id_user03 = message_send(
        user03["token"], channel_id_02, "message 2 by user 3"
    )
    message_3_id_user03 = message_send(
        user03["token"], channel_id_03, "message 3 by user 3"
    )

    message_remove(user02["token"], message_1_id_user02["message_id"])
    assert message_1_id_user02["message_id"] not in [
        x["message_id"]
        for x in database["channels"][channel_id_01]["messages"].values()
    ]
    message_remove(user02["token"], message_2_id_user02["message_id"])
    assert message_2_id_user02["message_id"] not in [
        x["message_id"]
        for x in database["channels"][channel_id_02]["messages"].values()
    ]
    message_remove(user02["token"], message_3_id_user02["message_id"])
    assert message_3_id_user02["message_id"] not in [
        x["message_id"]
        for x in database["channels"][channel_id_03]["messages"].values()
    ]

    message_remove(user03["token"], message_1_id_user03["message_id"])
    assert message_1_id_user03["message_id"] not in [
        x["message_id"]
        for x in database["channels"][channel_id_01]["messages"].values()
    ]
    message_remove(user03["token"], message_2_id_user03["message_id"])
    assert message_2_id_user03["message_id"] not in [
        x["message_id"]
        for x in database["channels"][channel_id_02]["messages"].values()
    ]
    message_remove(user03["token"], message_3_id_user03["message_id"])
    assert message_3_id_user03["message_id"] not in [
        x["message_id"]
        for x in database["channels"][channel_id_03]["messages"].values()
    ]

    # No messages left in either of the three channels
    assert (
        bool(channel_messages(user01["token"], channel_id_01, 0)["messages"]) == False
    )
    assert (
        bool(channel_messages(user01["token"], channel_id_02, 0)["messages"]) == False
    )
    assert (
        bool(channel_messages(user01["token"], channel_id_03, 0)["messages"]) == False
    )


# runs the test with is_public = True and is_public = False
# https://docs.pytest.org/en/stable/parametrize.html
@pytest.mark.parametrize("is_public", (True, False))
def test_message_remove_admin(is_public):
    clear()
    admin, usera = register_n_users(2, include_admin=True)

    channel_id = channels_create(usera["token"], "", is_public)["channel_id"]
    message_id = message_send(usera["token"], channel_id, "hello world")["message_id"]

    # admin removes the message
    message_remove(admin["token"], message_id)
    assert len(channel_messages(usera["token"], channel_id, start=0)["messages"]) == 0

    # admin joins the channel as a member
    channel_join(admin["token"], channel_id)

    # user a sends an other message
    message_id = message_send(usera["token"], channel_id, "where is my message gone?")[
        "message_id"
    ]

    # admin removes the message again
    message_remove(admin["token"], message_id)
    assert len(channel_messages(usera["token"], channel_id, start=0)["messages"]) == 0

    # admin joins the channel as an owner
    channel_addowner(admin["token"], channel_id, admin["u_id"])

    # user a sends an other message
    message_id = message_send(usera["token"], channel_id, "oh you nasty admin")[
        "message_id"
    ]

    # admin removes the message again
    message_remove(admin["token"], message_id)
    assert len(channel_messages(usera["token"], channel_id, start=0)["messages"]) == 0


@pytest.mark.parametrize("is_public", (True, False))
def test_message_remove_out_of_channel(is_public):
    clear()

    usera, userb = register_n_users(2)

    channel_id = channels_create(usera["token"], "", is_public)["channel_id"]
    channel_invite(usera["token"], channel_id, userb["u_id"])

    id1 = message_send(usera["token"], channel_id, "message from A!")["message_id"]
    id2 = message_send(userb["token"], channel_id, "message from B!")["message_id"]

    channel_leave(usera["token"], channel_id)
    channel_leave(userb["token"], channel_id)

    with pytest.raises(AccessError):
        message_remove(usera["token"], id1)

    with pytest.raises(AccessError):
        message_remove(userb["token"], id2)


##################################################################################
#                           Tests for message_send                               #
##################################################################################


def test_send_one_message():
    clear()

    usera = auth_register("email@a.com", "averylongpassword", "A", "LastA")
    channel_id = channels_create(usera["token"], "channela", is_public=True)[
        "channel_id"
    ]

    time_before_message_send = time.time()

    message_details = message_send(usera["token"], channel_id, "first message")
    assert "message_id" in message_details
    assert isinstance(message_details["message_id"], int)

    messages = channel_messages(usera["token"], channel_id, start=0)["messages"]
    assert messages[0]["u_id"] == usera["u_id"]
    assert messages[0]["message"] == "first message"
    assert messages[0]["time_created"] >= time_before_message_send


def test_message_send_access_error():
    clear()

    usera = auth_register("email@a.com", "averylongpassword", "A", "LastA")
    userb = auth_register("email@b.com", "averylongpassword", "b", "LastB")
    public_channel_id = channels_create(usera["token"], "channela", is_public=True)[
        "channel_id"
    ]
    private_channel_id = channels_create(usera["token"], "channelb", is_public=False)[
        "channel_id"
    ]

    with pytest.raises(AccessError):
        message_send(userb["token"], public_channel_id, "first message")

    with pytest.raises(AccessError):
        message_send(userb["token"], private_channel_id, "second message")

    # generate invalid channel id
    invalid_id = -1
    while invalid_id == public_channel_id or invalid_id == private_channel_id:
        invalid_id -= 1

    with pytest.raises(InputError):
        message_send(userb["token"], invalid_id, "third message")

    with pytest.raises(InputError):
        message_send(usera["token"], invalid_id, "fourth message")


def test_send_message_too_long():
    clear()

    usera = auth_register("email@a.com", "averylongpassword", "A", "LastA")
    channel_id = channels_create(usera["token"], "channela", is_public=True)[
        "channel_id"
    ]

    # shouldn't cause any problem
    message_send(usera["token"], channel_id, "a" * 1000)

    with pytest.raises(InputError):
        message_send(usera["token"], channel_id, "a" * 1001)

    # just to be safe
    with pytest.raises(InputError):
        message_send(usera["token"], channel_id, "a" * 1021)


def test_message_send_multiple_messages():
    clear()

    usera = auth_register("email@a.com", "averylongpassword", "A", "LastA")
    channel_id = channels_create(usera["token"], "channela", is_public=True)[
        "channel_id"
    ]

    time_before_message_send = time.time()

    message_send(usera["token"], channel_id, "first message")
    message_send(usera["token"], channel_id, "second message")
    message_send(usera["token"], channel_id, "third message")

    messages = channel_messages(usera["token"], channel_id, start=0)["messages"]

    assert len(messages) == 3

    assert messages[0]["message"] == "third message"
    assert messages[1]["message"] == "second message"
    assert messages[2]["message"] == "first message"

    message_ids = []
    for message in messages:
        assert message["u_id"] == usera["u_id"]
        assert message["time_created"] >= time_before_message_send

        # make sure all the ids are unique
        assert message["message_id"] not in message_ids
        message_ids.append(message["message_id"])


# TODO: test_message_send_member_but_not_owner (need to have channel join, not yet on this branch)
# TODO: test_message_send_multiple_members (need channel_join)

##################################################################################
#                           Tests for message_edit                               #
##################################################################################
def test_edit_invalid_user_token():
    clear()
    user = register_n_users(1)

    # Create a new channel
    channel = channels_create(user["token"], "channel01", is_public=True)
    # User sends a message
    message = message_send(user["token"], channel["channel_id"], "test message")
    # Non-existent user tries to edit the message
    with pytest.raises(AccessError):
        assert message_edit(INVALID_USER_TOKEN, message["message_id"], "edited message")


def test_edit_invalid_message_id():
    clear()
    user = register_n_users(1)

    # Create a new channel
    channel = channels_create(user["token"], "channel01", is_public=True)
    # User sends a message
    message_send(user["token"], channel["channel_id"], "test message")
    # User tries to edit message with an invalid message id (doesn't exist)
    with pytest.raises(AccessError):
        assert message_edit(user["token"], INVALID_MESSAGE_ID, "edited message")


# User tries to edit a message that they are not authorised to edit
def test_edit_unauthorised_user():
    clear()
    user01, user02 = register_n_users(2)

    # Create channel with message from user01
    channel = channels_create(user01["token"], "channel", is_public=True)
    channel_join(user02["token"], channel["channel_id"])
    message = message_send(user01["token"], channel["channel_id"], "test message")
    # User02 tries to edit message from user01
    with pytest.raises(AccessError):
        message_edit(user02["token"], message["message_id"], "edited message")


# Test that the owner of the flockr can edit any message
def test_edit_owner_flock_permissions():
    clear()
    user01, user02 = register_n_users(2)

    # Create a new channel with user01 as admin
    channel = channels_create(user01["token"], "channel", is_public=True)
    channel_join(user02["token"], channel["channel_id"])

    message = message_send(user02["token"], channel["channel_id"], "test message")
    message_edit(user01["token"], message["message_id"], "edited message")

    # Message stil exists and is edited
    assert message["message_id"] in [
        x["message_id"]
        for x in database["channels"][channel["channel_id"]]["messages"].values()
    ]

    assert (
        database["channels"][channel["channel_id"]]["messages"][message["message_id"]][
            "message"
        ]
        == "edited message"
    )


# Test that the owner of a channel can remove any message
def test_edit_owner_channel_permissions():
    clear()
    user01, user02, user03 = register_n_users(3)

    channels_create(user01["token"], "channel01", is_public=True)
    channel02 = channels_create(user02["token"], "channel02", is_public=True)
    channel_join(user03["token"], channel02["channel_id"])

    message = message_send(user03["token"], channel02["channel_id"], "test message")
    message_edit(user02["token"], message["message_id"], "edited message")

    assert (
        database["channels"][channel02["channel_id"]]["messages"][
            message["message_id"]
        ]["message"]
        == "edited message"
    )


# If edited message is empty string, message is deleted
def test_edit_empty_string():
    clear()
    user = register_n_users(1)

    # Create a new channel
    channel = channels_create(user["token"], "channel01", is_public=True)
    # User sends a message
    message = message_send(user["token"], channel["channel_id"], "test message")
    message_edit(user["token"], message["message_id"], "")
    assert message["message_id"] not in [
        x["message_id"]
        for x in database["channels"][channel["channel_id"]]["messages"].values()
    ]


# Edited message exceeds 1000 characters
def test_edit_exceeds_1000_char():
    clear()
    user = register_n_users(1)

    # Create a new channel
    channel = channels_create(user["token"], "channel01", is_public=True)
    # User sends a message
    message = message_send(user["token"], channel["channel_id"], "test message")
    edited_message = "a" * 1001
    with pytest.raises(InputError):
        assert message_edit(user["token"], message["message_id"], edited_message)


def test_edit_continuous_send():
    clear()
    user = register_n_users(1)
    channel_id = channels_create(user["token"], "channela", is_public=True)[
        "channel_id"
    ]

    for i in range(1, 50):
        message = message_send(user["token"], channel_id, "message " + str(i))
        message_edit(user["token"], message["message_id"], "edited message " + str(i))
        assert channel_messages(user["token"], channel_id, 0)["messages"][0][
            "message"
        ] == "edited message " + str(i)


@pytest.mark.parametrize("is_public", (True, False))
def test_message_edit_admin(is_public):
    clear()
    admin, usera = register_n_users(2, include_admin=True)

    channel_id = channels_create(usera["token"], "", is_public)["channel_id"]
    message_id = message_send(usera["token"], channel_id, "hello world")["message_id"]

    # admin removes the message
    message_edit(admin["token"], message_id, "admin edit #1")
    assert (
        channel_messages(usera["token"], channel_id, start=0)["messages"][0]["message"]
        == "admin edit #1"
    )

    # admin joins the channel as a member
    channel_join(admin["token"], channel_id)

    # user a sends an other message
    message_id = message_send(usera["token"], channel_id, "where is my message gone?")[
        "message_id"
    ]

    # admin removes the message again
    message_edit(admin["token"], message_id, "admin edit #2")
    assert (
        channel_messages(usera["token"], channel_id, start=0)["messages"][0]["message"]
        == "admin edit #2"
    )

    # admin joins the channel as an owner
    channel_addowner(admin["token"], channel_id, admin["u_id"])

    # user a sends an other message
    message_id = message_send(usera["token"], channel_id, "oh you nasty admin")[
        "message_id"
    ]

    # admin removes the message again
    message_edit(admin["token"], message_id, "admin edit #3")
    assert (
        channel_messages(usera["token"], channel_id, start=0)["messages"][0]["message"]
        == "admin edit #3"
    )


@pytest.mark.parametrize("is_public", (True, False))
def test_message_edit_out_of_channel(is_public):
    clear()

    usera, userb = register_n_users(2)

    channel_id = channels_create(usera["token"], "", is_public)["channel_id"]
    channel_invite(usera["token"], channel_id, userb["u_id"])

    id1 = message_send(usera["token"], channel_id, "message from A!")["message_id"]
    id2 = message_send(userb["token"], channel_id, "message from B!")["message_id"]

    channel_leave(usera["token"], channel_id)
    channel_leave(userb["token"], channel_id)

    with pytest.raises(AccessError):
        message_edit(usera["token"], id1, "edit 1")

    with pytest.raises(AccessError):
        message_edit(userb["token"], id2, "edit 2")
