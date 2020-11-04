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
from standup import (
    standup_start,
    standup_active,
    standup_send
)
from test_helpers import register_n_users, assert_contains_users_id
from database import database
from other import clear

from threading import Timer
import time
import pytest
from error import AccessError, InputError

messages = []
time = time.time()

def get_time():
    global time
    time = time.time()

def collect_message(token, channel_id):
    global messages
    messages = channel_messages(token, channel_id, 0)["messages"]
    
def check_active():


def test_start_simple():
    clear()
    user1, user2 = register_n_users(2)

    channel = channels_create(user1["token"], "channel1", is_public=True)
    channel_join(user2["token"], channel["channel_id"])

    t1 = Timer(2, collect_message, [user1["token"], channel["channel_id"]])
    t2 = Timer(1, get_time)
    t2.start()
    standup_start(user1["token"], channel["channel_id"], 1)
    standup_send(user1["token"], channel["channel_id"], "test1")
    standup_send(user2["token"], channel["channel_id"], "test2")

    t1.start()

    assert len(messages) == 2
    for message, i in messages, range(1):
        assert message["time_created"] == time
        assert message["message"] == "test" + str(i)

def test_active_simple():
    clear()
    user1 = register_n_users(1)
    channel = channels_create(user1["token"], "channel1", is_public=True)

    standup_start(user1["token"], channel["channel_id"], 1)
    assert standup_active(user1["token"], channel["channel_id"])["is_active"] == True

    time.sleep(2)
    assert standup_active(user1["token"], channel["channel_id"])["is_active"] == False



