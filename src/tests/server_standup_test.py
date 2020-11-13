from test_helpers import url, http_register_n_users
from error import AccessError, InputError
import pytest

import requests
import json
from time import sleep, time

##################################################################################
#                          Tests for standup_start                               #
##################################################################################


def test_standup_start_simple(url):
    requests.delete(url + "clear")
    user1, user2 = http_register_n_users(url, 2)

    # Create channel and join: user1, 2 are in the same channel
    channel = requests.post(
        url + "channels/create",
        json={"token": user1["token"], "name": "channel_01", "is_public": True},
    ).json()

    requests.post(
        url + "channel/join",
        json={"token": user2["token"], "channel_id": channel["channel_id"]},
    )

    # Start the standup period
    standup = requests.post(
        url + "standup/start",
        json={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "length": 1,
        },
    ).json()
    assert standup["time_finish"] == round(time() + 1)

    # Send two standup message
    requests.post(
        url + "standup/send",
        json={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "message": "test1",
        },
    )
    requests.post(
        url + "standup/send",
        json={
            "token": user2["token"],
            "channel_id": channel["channel_id"],
            "message": "test2",
        },
    )

    # Assert the messages are empty
    messages = requests.get(
        url + "channel/messages",
        params={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "start": 0,
        },
    ).json()["messages"]
    assert len(messages) == 0

    # Assert the two message has been sent when the standup period finishes
    sleep(3)
    messages = requests.get(
        url + "channel/messages",
        params={
            "token": user2["token"],
            "channel_id": channel["channel_id"],
            "start": 0,
        },
    ).json()["messages"]
    assert len(messages) == 1

    # Get user1 and user2's handle
    user1_profile = requests.get(
        url + "user/profile", params={"token": user1["token"], "u_id": user1["u_id"]}
    ).json()["user"]
    user1_handle = user1_profile["handle_str"]
    user2_handle = requests.get(
        url + "user/profile", params={"token": user2["token"], "u_id": user2["u_id"]}
    ).json()["user"]["handle_str"]

    # Assert that the message content is as expected
    assert messages[0]["message"] == f"{user1_handle}: test1\n{user2_handle}: test2"
    assert messages[0]["u_id"] == user1_profile["u_id"]


def test_standup_start_invalid_channel_id(url):
    requests.delete(url + "clear")
    user1 = http_register_n_users(url, 1)

    invalid_channel_id = -1

    response = requests.post(
        url + "standup/start",
        json={"token": user1["token"], "channel_id": invalid_channel_id, "length": 1},
    )

    # Channel id is invalid
    assert response.status_code == 400


def test_standup_start_standup_is_already_running(url):
    requests.delete(url + "clear")
    user1 = http_register_n_users(url, 1)

    # Create channel
    channel = requests.post(
        url + "channels/create",
        json={"token": user1["token"], "name": "channel_01", "is_public": True},
    ).json()

    # Start a standup
    requests.post(
        url + "standup/start",
        json={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "length": 1,
        },
    )

    # Another standup when there's one already running
    response = requests.post(
        url + "standup/start",
        json={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "length": 1,
        },
    )
    assert response.status_code == 400


def test_standup_start_no_message_sent(url):
    requests.delete(url + "clear")
    user1 = http_register_n_users(url, 1)

    # Create channel
    channel = requests.post(
        url + "channels/create",
        json={"token": user1["token"], "name": "channel_01", "is_public": True},
    ).json()

    # Start a standup
    requests.post(
        url + "standup/start",
        json={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "length": 1,
        },
    )

    # Assert the messages are empty
    messages = requests.get(
        url + "channel/messages",
        params={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "start": 0,
        },
    ).json()["messages"]
    assert len(messages) == 0


##################################################################################
#                         Tests for standup_active                               #
##################################################################################


def test_standup_active_simple(url):
    requests.delete(url + "clear")
    user1 = http_register_n_users(url, 1)

    # Create channel
    channel = requests.post(
        url + "channels/create",
        json={"token": user1["token"], "name": "channel_01", "is_public": True},
    ).json()

    # Start a standup
    requests.post(
        url + "standup/start",
        json={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "length": 1,
        },
    )

    # Assert the return value of standup_active is correct
    response = requests.get(
        url + "standup/active",
        params={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
        },
    ).json()

    assert response["is_active"] == True
    assert response["time_finish"] == round(time() + 1)

    sleep(2)
    response = requests.get(
        url + "standup/active",
        params={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
        },
    ).json()
    assert response["is_active"] == False
    assert response["time_finish"] == None


def test_standup_active_invalid_channel_id(url):
    requests.delete(url + "clear")
    user1 = http_register_n_users(url, 1)

    # Create channel
    channel = requests.post(
        url + "channels/create",
        json={"token": user1["token"], "name": "channel_01", "is_public": True},
    ).json()

    # Start a standup
    requests.post(
        url + "standup/start",
        json={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "length": 1,
        },
    )

    # Check active with a invlid channel id
    invalid_channel_id = -1
    response = requests.get(
        url + "standup/active",
        params={
            "token": user1["token"],
            "channel_id": invalid_channel_id,
        },
    )
    assert response.status_code == 400


##################################################################################
#                           Tests for standup_send                               #
##################################################################################


def test_standup_send_invalid_channel_id(url):
    requests.delete(url + "clear")
    user1 = http_register_n_users(url, 1)

    # Create channel
    channel = requests.post(
        url + "channels/create",
        json={"token": user1["token"], "name": "channel_01", "is_public": True},
    ).json()

    # Start a standup
    requests.post(
        url + "standup/start",
        json={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "length": 1,
        },
    )

    # Send with invalid channel id
    invalid_channel_id = -1
    response = requests.post(
        url + "standup/send",
        json={
            "token": user1["token"],
            "channel_id": invalid_channel_id,
            "message": "test",
        },
    )
    assert response.status_code == 400


def test_standup_send_long_message(url):
    requests.delete(url + "clear")
    user1 = http_register_n_users(url, 1)

    # Create channel
    channel = requests.post(
        url + "channels/create",
        json={"token": user1["token"], "name": "channel_01", "is_public": True},
    ).json()

    # Start a standup
    requests.post(
        url + "standup/start",
        json={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "length": 1,
        },
    )

    requests.post(
        url + "standup/send",
        json={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "message": "a" * 1000,
        },
    )

    # Too long messages
    response = requests.post(
        url + "standup/send",
        json={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "message": "a" * 1001,
        },
    )
    assert response.status_code == 400

    response = requests.post(
        url + "standup/send",
        json={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "message": "a" * 1021,
        },
    )
    assert response.status_code == 400


def test_standup_send_no_active_standup(url):
    requests.delete(url + "clear")
    user1 = http_register_n_users(url, 1)

    # Create channel
    channel = requests.post(
        url + "channels/create",
        json={"token": user1["token"], "name": "channel_01", "is_public": True},
    ).json()

    # No active standup
    response = requests.post(
        url + "standup/send",
        json={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "message": "test",
        },
    )
    assert response.status_code == 400


def test_standup_send_AccessError(url):
    requests.delete(url + "clear")
    user1, user2 = http_register_n_users(url, 2)

    # Create channel
    channel = requests.post(
        url + "channels/create",
        json={"token": user1["token"], "name": "channel_01", "is_public": True},
    ).json()

    # Start a standup
    requests.post(
        url + "standup/start",
        json={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "length": 1,
        },
    )

    # User2 is not a member of the channel
    response = requests.post(
        url + "standup/send",
        json={
            "token": user2["token"],
            "channel_id": channel["channel_id"],
            "message": "test",
        },
    )
    assert response.status_code == 403


##################################################################################
#                          Complex Integration Test                              #
##################################################################################


def test_standup_start_complex(url):
    requests.delete(url + "clear")
    user1, user2, user3 = http_register_n_users(url, 3)

    # Create channel and join: user1, 2 are in the same channel
    channel = requests.post(
        url + "channels/create",
        json={"token": user1["token"], "name": "channel_01", "is_public": True},
    ).json()

    requests.post(
        url + "channel/join",
        json={"token": user2["token"], "channel_id": channel["channel_id"]},
    )

    ######################################
    #           The first standup        #
    ######################################
    standup = requests.post(
        url + "standup/start",
        json={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "length": 1,
        },
    ).json()

    # Assert the standup is activated succesfullly
    assert standup["time_finish"] == round(time() + 1)
    assert (
        requests.get(
            url + "standup/active",
            params={
                "token": user1["token"],
                "channel_id": channel["channel_id"],
            },
        ).json()["is_active"]
        == True
    )

    sleep(2)

    # Assert the messages are empty
    messages = requests.get(
        url + "channel/messages",
        params={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "start": 0,
        },
    ).json()["messages"]
    assert len(messages) == 0

    # Assert that standup has finished
    response = requests.get(
        url + "standup/active",
        params={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
        },
    ).json()
    assert response["is_active"] == False
    assert response["time_finish"] == None

    ######################################
    #          The second standup        #
    ######################################
    standup = requests.post(
        url + "standup/start",
        json={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "length": 3,
        },
    ).json()

    # Assert the standup is activated succesfullly
    assert standup["time_finish"] == round(time() + 3)

    # Assert that standup active return the right value
    response = requests.get(
        url + "standup/active",
        params={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
        },
    ).json()
    assert response["is_active"] == True
    assert response["time_finish"] == round(time() + 3)

    # Send two standup message
    requests.post(
        url + "standup/send",
        json={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "message": "test1",
        },
    )
    requests.post(
        url + "standup/send",
        json={
            "token": user2["token"],
            "channel_id": channel["channel_id"],
            "message": "test2",
        },
    )

    # User3 is not a member of the channel
    response = requests.post(
        url + "standup/send",
        json={
            "token": user3["token"],
            "channel_id": channel["channel_id"],
            "message": "test",
        },
    )
    assert response.status_code == 403

    # A third message
    requests.post(
        url + "standup/send",
        json={
            "token": user2["token"],
            "channel_id": channel["channel_id"],
            "message": "test3",
        },
    )

    # Assert the two message has been sent when the standup period finishes
    sleep(4)
    messages = requests.get(
        url + "channel/messages",
        params={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "start": 0,
        },
    ).json()["messages"]
    assert len(messages) == 1

    # Assert that the standup period has finishes
    response = requests.get(
        url + "standup/active",
        params={
            "token": user2["token"],
            "channel_id": channel["channel_id"],
        },
    ).json()
    assert response["is_active"] == False
    assert response["time_finish"] == None

    # Assert that the message is as expexted
    user1_profile = requests.get(
        url + "user/profile", params={"token": user1["token"], "u_id": user1["u_id"]}
    ).json()["user"]
    user2_profile = requests.get(
        url + "user/profile", params={"token": user2["token"], "u_id": user2["u_id"]}
    ).json()["user"]

    user1_handle = user1_profile["handle_str"]
    user2_handle = user2_profile["handle_str"]

    assert (
        messages[0]["message"]
        == f"{user1_handle}: test1\n{user2_handle}: test2\n{user2_handle}: test3"
    )
    assert messages[0]["u_id"] == user1_profile["u_id"]

    # No standup is active
    response = requests.post(
        url + "standup/send",
        json={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "message": "test",
        },
    )
    assert response.status_code == 400

    ######################################
    #           The third standup        #
    ######################################
    standup = requests.post(
        url + "standup/start",
        json={
            "token": user2["token"],
            "channel_id": channel["channel_id"],
            "length": 1,
        },
    ).json()

    # Assert the standup is activated succesfullly
    assert standup["time_finish"] == round(time() + 1)

    # Assert that standup active return the right value
    response = requests.get(
        url + "standup/active",
        params={
            "token": user2["token"],
            "channel_id": channel["channel_id"],
        },
    ).json()
    assert response["is_active"] == True
    assert response["time_finish"] == round(time() + 1)

    # User3 join the channel during standup
    requests.post(
        url + "channel/join",
        json={"token": user3["token"], "channel_id": channel["channel_id"]},
    )

    # Send two standup message
    requests.post(
        url + "standup/send",
        json={
            "token": user1["token"],
            "channel_id": channel["channel_id"],
            "message": "LMAO",
        },
    )
    requests.post(
        url + "standup/send",
        json={
            "token": user2["token"],
            "channel_id": channel["channel_id"],
            "message": "LOL",
        },
    )
    requests.post(
        url + "standup/send",
        json={
            "token": user3["token"],
            "channel_id": channel["channel_id"],
            "message": "WTF\n",
        },
    )

    sleep(2)
    # Assert that there are two messages now
    messages = requests.get(
        url + "channel/messages",
        params={
            "token": user3["token"],
            "channel_id": channel["channel_id"],
            "start": 0,
        },
    ).json()["messages"]
    assert len(messages) == 2

    # Get user3's handle
    user3_handle = requests.get(
        url + "user/profile", params={"token": user3["token"], "u_id": user3["u_id"]}
    ).json()["user"]["handle_str"]

    # Assert that the message is as expexted
    assert (
        messages[0]["message"]
        == f"{user1_handle}: LMAO\n{user2_handle}: LOL\n{user3_handle}: WTF\n"
    )
    assert messages[0]["u_id"] == user2_profile["u_id"]
