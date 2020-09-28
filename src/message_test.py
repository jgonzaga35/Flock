import time
from auth import auth_register
from database import clear_database
from channels import channels_create
from channel import channel_messages
from message import message_send

def test_send_one_message():
    clear_database()

    usera = auth_register("email@a.com", "averylongpassword", "A", "LastA")
    userb = auth_register("email@b.com", "averylongpassword", "B", "LastB")

    channel_id = channels_create(usera['token'], "channela", is_public=True)['channel_id']

    time_before_message_send = time.time()

    message_details = message_send(usera['token'], channel_id, 'first message')
    assert 'message_id' in message_details
    assert isinstance(message_details['message_id'], int)

    messages = channel_messages(usera['token'], channel_id, start=0)['messages']
    assert messages[0]['u_id'] == usera['token']
    assert messages[0]['message'] == 'first message'
    assert messages[0]['time_created'] >= time_before_message_send

