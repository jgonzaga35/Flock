import pytest
from test_helpers import register_n_users, assert_contains_users_id
from channel import channel_join, channel_details, channel_messages, channel_addowner
from message import message_send, message_remove
from channels import channels_create
from database import clear_database


# runs the test with is_public = True and is_public = False
# https://docs.pytest.org/en/stable/parametrize.html
@pytest.mark.parametrize("is_public", (True, False))
def test_message_remove_admin(is_public):
    clear_database()
    admin, usera = register_n_users(2, include_admin=True)

    channel_id = channels_create(usera["token"], "", is_public)["channel_id"]
    message_id = message_send(usera["token"], channel_id, "hello world")["message_id"]

    # admin removes the message
    message_remove(admin["token"], message_id)
    assert len(channel_messages(usera["token"], channel_id)["messages"]) == 0

    # admin joins the channel as a member
    channel_join(admin["token"], channel_id)

    # user a sends an other message
    message_id = message_send(usera["token"], channel_id, "where is my message gone?")

    # admin removes the message again
    message_remove(admin["token"], message_id)
    assert len(channel_messages(usera["token"], channel_id)["messages"]) == 0

    # admin joins the channel as an owner
    channel_addowner(admin["token"], channel_id)

    # user a sends an other message
    message_id = message_send(usera["token"], channel_id, "oh you nasty admin")

    # admin removes the message again
    message_remove(admin["token"], message_id)
    assert len(channel_messages(usera["token"], channel_id)["messages"]) == 0
