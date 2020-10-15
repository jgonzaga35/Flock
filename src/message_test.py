from message import message_send, message_remove, message_edit
from auth import auth_register
from channel import channel_messages, channel_join
from channels import channels_create, channels_list
from test_helpers import register_n_users
from database import database, clear_database

import time
import pytest
from error import AccessError, InputError

INVALID_USER_TOKEN = -1
INVALID_MESSAGE_ID = -1
CHAR_1000_STR = """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
    Nullam ac purus non diam elementum commodo. Fusce nec leo eros. 
    Nullam a augue iaculis, convallis velit eu, porta elit. 
    Nunc vitae sollicitudin sem, sed varius nibh. 
    Donec aliquam sollicitudin nunc et dignissim. 
    Morbi sed luctus arcu, sed consectetur odio. 
    Duis et mauris sollicitudin, lacinia mauris in, posuere turpis. 
    Curabitur pellentesque ultrices odio, eu semper risus pretium in. 
    Nam iaculis, purus in ultrices porta, metus ex sagittis orci, 
    in ultricies ipsum turpis nec justo. Morbi nec est est. 
    Duis lacinia ex vel nibh tristique, at ultricies nulla molestie.
    In vel massa quis ipsum venenatis interdum id sit amet urna. 
    Pellentesque mattis lacinia quam, nec posuere purus volutpat id. 
    Morbi at ultrices purus, eu aliquet sapien. 
    Etiam risus odio, convallis id sagittis nec, tincidunt ac nisl. 
    Aliquam interdum, turpis eu eleifend varius, 
    mi nunc pellentesque massa, et vulputate nulla magna ac neque. 
    Morbi eu pharetra ante. Duis quis fermentum mi. 
    """


def test_send_one_message():
    clear_database()

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
    clear_database()

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
    clear_database()

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
    clear_database()

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


def test_message_remove():
    # just to make coverage happy
    message_remove(-1, -1)


##################################################################################
#                           Tests for message_edit                               #
##################################################################################
def test_edit_invalid_user_token():
    clear_database()
    user = register_n_users(1)

    # Create a new channel
    channel = channels_create(user["token"], "channel01", is_public=True)
    # User sends a message
    message = message_send(user["token"], channel["channel_id"], "test message")
    # Non-existent user tries to edit the message
    with pytest.raises(AccessError):
        assert message_edit(INVALID_USER_TOKEN, message["message_id"], "edited message")


def test_edit_invalid_message_id():
    clear_database()
    user = register_n_users(1)

    # Create a new channel
    channel = channels_create(user["token"], "channel01", is_public=True)
    # User sends a message
    message_send(user["token"], channel["channel_id"], "test message")
    # User tries to edit message with an invalid message id (doesn't exist)
    with pytest.raises(InputError):
        assert message_edit(user["token"], INVALID_MESSAGE_ID, "edited message")


# User tries to edit a message that they are not authorised to edit
def test_edit_unauthorised_user():
    clear_database()
    user01, user02 = register_n_users(2)

    # Create channel with message from user01
    channel = channels_create(user01["token"], "channel", is_public=True)
    channel_join(user02["token"], channel["channel_id"])
    message = message_send(user01["token"], channel["channel_id"], "test message")
    # User02 tries to remove message from user01
    with pytest.raises(AccessError):
        message_edit(user02["token"], message["message_id"], "edited message")


# Test that the owner of the flockr can edit any message
def test_edit_owner_flock_permissions():
    clear_database()
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
    clear_database()
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
    clear_database()
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


# Edited message exceeds 1000 characters - commented out until #81 clarified
# def test_edit_exceeds_1000_char():
#     clear_database()
#     user = register_n_users(1)

#     # Create a new channel
#     channel = channels_create(user["token"], "channel01", is_public=True)
#     # User sends a message
#     message = message_send(user["token"], channel["channel_id"], "test message")

#     with pytest.raises(InputError):
#         assert message_edit(user["token"], message["message_id"], CHAR_1000_STR)


def test_edit_continuous_send():
    clear_database()
    user = register_n_users(1)
    channel_id = channels_create(user["token"], "channela", is_public=True)[
        "channel_id"
    ]

    for i in range(1, 50):
        message = message_send(user["token"], channel_id, "message " + str(i))
        message_edit(user["token"], message["message_id"], "edited message " + str(i))
        assert (
            database["channels"][channel_id]["messages"][
                message["message_id"]
            ]["message"]
            == "edited message " + str(i)
        )
        