# Function interface
from auth import auth_register
from message import message_send, message_remove, message_edit
from channel import (
    channel_join,
    channel_messages,
)
from channels import channels_create
from standup import standup_start, standup_active, standup_send
from user import user_profile

# Testing relate (Local)
from test_helpers import register_n_users
from other import clear, search
from error import AccessError, InputError

# Testing relate (External)
import pytest
from threading import Timer
from time import sleep, time


##################################################################################
#                          Tests for standup_start                               #
##################################################################################


def test_standup_start_simple():
    clear()
    user1, user2 = register_n_users(2)

    # Create channel and join
    channel = channels_create(user1["token"], "channel1", is_public=True)
    channel_join(user2["token"], channel["channel_id"])

    # Start the standup period
    standup = standup_start(user1["token"], channel["channel_id"], 1)
    assert round(standup["time_finish"]) == 1

    # Send two standup message
    standup_send(user1["token"], channel["channel_id"], "test1")
    standup_send(user2["token"], channel["channel_id"], "test2")

    # Assert the messages are empty
    messages = channel_messages(user1["token"], channel["channel_id"], 0)["messages"]
    assert len(messages) == 0

    # Assert the two message has been sent when the standup period finishes
    sleep(2)
    messages = channel_messages(user1["token"], channel["channel_id"], 0)["messages"]
    assert len(messages) == 1

    user1_handle = user_profile(user1["token"], user1["u_id"])["user"]["handle_str"]
    user2_handle = user_profile(user2["token"], user2["u_id"])["user"]["handle_str"]
    assert messages[0]["message"] == f"{user1_handle}: test1\n{user2_handle}: test2"
    assert (
        messages[0]["u_id"]
        == user_profile(user1["token"], user1["u_id"])["user"]["u_id"]
    )


def test_standup_start_invalid_channel_id():
    clear()
    user1 = register_n_users(1)

    invalid_channel_id = -1
    with pytest.raises(InputError):
        standup_start(user1["token"], invalid_channel_id, 1)


def test_standup_start_standup_is_already_running():
    clear()
    user1 = register_n_users(1)

    channel = channels_create(user1["token"], "channel1", is_public=True)

    standup_start(user1["token"], channel["channel_id"], 1)

    with pytest.raises(InputError):
        standup_start(user1["token"], channel["channel_id"], 1)


def test_standup_start_no_message_sent():
    clear()
    user1 = register_n_users(1)

    channel = channels_create(user1["token"], "channel1", is_public=True)

    standup_start(user1["token"], channel["channel_id"], 1)

    messages = channel_messages(user1["token"], channel["channel_id"], 0)["messages"]
    assert len(messages) == 0


##################################################################################
#                         Tests for standup_active                               #
##################################################################################


def test_standup_active_simple():
    clear()
    user1 = register_n_users(1)
    channel = channels_create(user1["token"], "channel1", is_public=True)

    standup_start(user1["token"], channel["channel_id"], 1)

    # Assert the return value of standup_active is correct
    assert standup_active(user1["token"], channel["channel_id"])["is_active"] == True
    assert (
        round(standup_active(user1["token"], channel["channel_id"])["time_finish"]) == 1
    )

    sleep(2)
    assert standup_active(user1["token"], channel["channel_id"])["is_active"] == False
    assert standup_active(user1["token"], channel["channel_id"])["time_finish"] == None


def test_standup_active_invalid_channel_id():
    clear()
    user1 = register_n_users(1)

    channel = channels_create(user1["token"], "channel1", is_public=True)

    standup_start(user1["token"], channel["channel_id"], 1)

    invalid_channel_id = -1
    with pytest.raises(InputError):
        standup_active(user1["token"], invalid_channel_id)


##################################################################################
#                           Tests for standup_send                               #
##################################################################################


def test_standup_send_invalid_channel_id():
    clear()
    user1 = register_n_users(1)

    channel = channels_create(user1["token"], "channel1", is_public=True)

    standup_start(user1["token"], channel["channel_id"], 1)

    # Send with invalid channel id
    invalid_channel_id = -1
    with pytest.raises(InputError):
        standup_send(user1["token"], invalid_channel_id, "Test")


def test_standup_send_long_message():
    clear()
    user1 = register_n_users(1)

    channel = channels_create(user1["token"], "channel1", is_public=True)

    standup_start(user1["token"], channel["channel_id"], 2)

    standup_send(user1["token"], channel["channel_id"], "a" * 1000)

    with pytest.raises(InputError):
        standup_send(user1["token"], channel["channel_id"], "a" * 1001)

    with pytest.raises(InputError):
        standup_send(user1["token"], channel["channel_id"], "a" * 1020)


def test_standup_send_no_active_standup():
    clear()
    user1 = register_n_users(1)

    channel = channels_create(user1["token"], "channel1", is_public=True)

    with pytest.raises(InputError):
        standup_send(user1["token"], channel["channel_id"], "Test")


def test_standup_send_AccessError():
    clear()
    user1, user2 = register_n_users(2)

    channel = channels_create(user1["token"], "channel1", is_public=True)

    standup_start(user1["token"], channel["channel_id"], 2)

    # User2 is not a member of the channel
    with pytest.raises(AccessError):
        standup_send(user2["token"], channel["channel_id"], "Test")


##################################################################################
#                          Complex Integration Test                              #
##################################################################################


def test_standup_start_complex():
    clear()
    user1, user2, user3 = register_n_users(3)

    # Create channel and join
    channel = channels_create(user1["token"], "channel1", is_public=True)
    channel_join(user2["token"], channel["channel_id"])

    ######################################
    #           The first standup        #
    ######################################
    standup = standup_start(user1["token"], channel["channel_id"], 1)

    # Assert the standup is activated succesfullly
    assert round(standup["time_finish"]) == 1
    assert standup_active(user1["token"], channel["channel_id"])["is_active"] == True

    sleep(2)

    # Assert the messages are empty, standup has finished
    messages = channel_messages(user1["token"], channel["channel_id"], 0)["messages"]
    assert len(messages) == 0
    assert standup_active(user1["token"], channel["channel_id"])["is_active"] == False
    assert standup_active(user2["token"], channel["channel_id"])["time_finish"] == None

    ######################################
    #          The second standup        #
    ######################################
    standup = standup_start(user1["token"], channel["channel_id"], 3)

    # Assert the standup is activated succesfullly
    assert round(standup["time_finish"]) == 3
    assert standup_active(user1["token"], channel["channel_id"])["is_active"] == True
    assert (
        round(standup_active(user1["token"], channel["channel_id"])["time_finish"]) == 3
    )

    # Send two standup message
    standup_send(user1["token"], channel["channel_id"], "test1")
    standup_send(user2["token"], channel["channel_id"], "test2")

    # Unathorised User
    with pytest.raises(AccessError):
        standup_send(user3["token"], channel["channel_id"], "Test")

    # A third message
    standup_send(user2["token"], channel["channel_id"], "test3")

    # Assert the two message has been sent when the standup period finishes
    sleep(4)
    messages = channel_messages(user1["token"], channel["channel_id"], 0)["messages"]
    assert len(messages) == 1

    # Assert that the standup period has finishes
    assert standup_active(user1["token"], channel["channel_id"])["is_active"] == False
    assert standup_active(user1["token"], channel["channel_id"])["time_finish"] == None

    # Assert that the message is as expexted
    user1_handle = user_profile(user1["token"], user1["u_id"])["user"]["handle_str"]
    user2_handle = user_profile(user2["token"], user2["u_id"])["user"]["handle_str"]
    assert (
        messages[0]["message"]
        == f"{user1_handle}: test1\n{user2_handle}: test2\n{user2_handle}: test3"
    )
    assert (
        messages[0]["u_id"]
        == user_profile(user1["token"], user1["u_id"])["user"]["u_id"]
    )

    # No standup is active
    with pytest.raises(InputError):
        standup_send(user1["token"], channel["channel_id"], "Test")

    ######################################
    #           The third standup        #
    ######################################
    standup = standup_start(user2["token"], channel["channel_id"], 1)

    # Assert the standup is activated succesfullly
    assert round(standup["time_finish"]) == 1
    assert standup_active(user1["token"], channel["channel_id"])["is_active"] == True
    assert (
        round(standup_active(user2["token"], channel["channel_id"])["time_finish"]) == 1
    )

    # User3 join the channel during standup
    channel_join(user3["token"], channel["channel_id"])

    # Send two standup message
    standup_send(user1["token"], channel["channel_id"], "LMAO")
    standup_send(user2["token"], channel["channel_id"], "LOL")
    standup_send(user3["token"], channel["channel_id"], "WTF\n")

    sleep(2)
    # Assert that there are two messages now
    messages = channel_messages(user1["token"], channel["channel_id"], 0)["messages"]
    assert len(messages) == 2

    # Assert that the message is as expexted
    user3_handle = user_profile(user3["token"], user3["u_id"])["user"]["handle_str"]
    assert (
        messages[0]["message"]
        == f"{user1_handle}: LMAO\n{user2_handle}: LOL\n{user3_handle}: WTF\n"
    )
    assert (
        messages[0]["u_id"]
        == user_profile(user2["token"], user2["u_id"])["user"]["u_id"]
    )
