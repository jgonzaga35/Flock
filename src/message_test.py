import time
import pytest
from auth import auth_register
from database import clear_database
from channels import channels_create
from channel import channel_messages
from message import message_send
from error import AccessError

def test_send_one_message():
    clear_database()

    usera = auth_register("email@a.com", "averylongpassword", "A", "LastA")
    channel_id = channels_create(usera['token'], "channela", is_public=True)['channel_id']

    time_before_message_send = time.time()

    message_details = message_send(usera['token'], channel_id, 'first message')
    assert 'message_id' in message_details
    assert isinstance(message_details['message_id'], int)

    messages = channel_messages(usera['token'], channel_id, start=0)['messages']
    assert messages[0]['u_id'] == usera['token']
    assert messages[0]['message'] == 'first message'
    assert messages[0]['time_created'] >= time_before_message_send

def test_message_send_not_member():
    clear_database()

    usera = auth_register("email@a.com", "averylongpassword", "A", "LastA")
    userb = auth_register("email@b.com", "averylongpassword", "b", "LastB")
    channel_id = channels_create(usera['token'], "channela", is_public=True)['channel_id']

    with pytest.raises(AccessError):
        message_send(userb['token'], channel_id, 'first message')

def test_message_send_multiple_messages():
    clear_database()

    usera = auth_register("email@a.com", "averylongpassword", "A", "LastA")
    channel_id = channels_create(usera['token'], "channela", is_public=True)['channel_id']

    time_before_message_send = time.time()

    message_send(usera['token'], channel_id, "first message")
    message_send(usera['token'], channel_id, "second message")
    message_send(usera['token'], channel_id, "third message")

    messages = channel_messages(usera['token'], channel_id, start=0)['messages']

    assert len(messages) == 3

    assert messages[0]['message'] == "third message"
    assert messages[1]['message'] == 'second message'
    assert messages[2]['message'] == 'first message'

    for message in messages:
        assert message['u_id'] == usera['id']
        assert message['time_created'] >= time_before_message_send


# TODO: test_message_send_member_but_not_owner (need to have channel join, not yet on this branch)
# TODO: test_message_send_multiple_members (need channel_join) 