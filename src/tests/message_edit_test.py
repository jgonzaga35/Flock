import pytest
from test_helpers import register_n_users, assert_contains_users_id
from channel import channel_join, channel_details, channel_messages, channel_addowner
from message import message_send, message_edit
from channels import channels_create
from other import clear


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
