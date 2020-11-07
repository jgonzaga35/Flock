import json
import requests
from test_helpers import url, http_register_n_users


def test_react_succesfully(url):
    requests.delete(url + "clear")
    user_a, user_b = http_register_n_users(url, 2)
    public_channel_id = requests.post(
        url + "channels/create",
        json={"token": user_a["token"], "name": "public_channel", "is_public": True},
    ).json()["channel_id"]
    # user_b join the channel created by user_a
    requests.post(
        url + "channel/join",
        json={"token": user_b["token"], "channel_id": public_channel_id},
    )

    message_id = requests.post(
        url + "message/send",
        json={
            "token": user_a["token"],
            "channel_id": public_channel_id,
            "message": "Nice to see you mate",
        },
    ).json()["message_id"]
    # user_a react to his own message
    response = requests.post(
        url + "message/react",
        json={
            "token": user_a["token"],
            "message_id": message_id,
            "react_id": 1,
        },
    )
    assert response.status_code == 200
    # Message from the perspective of user_a
    message_a = requests.get(
        url + "channel/messages",
        params={
            "token": user_a["token"],
            "channel_id": public_channel_id,
            "start": 0,
        },
    ).json()["messages"][0]
    # user_a reacted
    assert message_a["reacts"][0]["is_this_user_reacted"] == True
    assert user_a["u_id"] in message_a["reacts"][0]["u_ids"]

    # Message from the perspective of user_b
    message_b = requests.get(
        url + "channel/messages",
        params={
            "token": user_b["token"],
            "channel_id": public_channel_id,
            "start": 0,
        },
    ).json()["messages"][0]
    # user_b haven't reacted
    assert message_b["reacts"][0]["is_this_user_reacted"] == False
    # user_b react to the message
    requests.post(
        url + "message/react",
        json={
            "token": user_b["token"],
            "message_id": message_id,
            "react_id": 1,
        },
    )
    message_b = requests.get(
        url + "channel/messages",
        params={
            "token": user_b["token"],
            "channel_id": public_channel_id,
            "start": 0,
        },
    ).json()["messages"][0]
    # user_b has reacted to the message
    assert message_b["reacts"][0]["is_this_user_reacted"] == True
    assert user_b["u_id"] in message_b["reacts"][0]["u_ids"]


def test_react_invalid_message_id_in_different_channel(url):
    """
    Test the situation where the user trying to react to a message but
    not in that channel
    """
    requests.delete(url + "clear")
    user_a, user_b = http_register_n_users(url, 2)
    # user_a create a channel
    requests.post(
        url + "channels/create",
        json={"token": user_a["token"], "name": "public_channel_a", "is_public": True},
    ).json()["channel_id"]
    # user_b create a channel and send message in his own channel
    public_channel_id_b = requests.post(
        url + "channels/create",
        json={"token": user_b["token"], "name": "public_channel_b", "is_public": True},
    ).json()["channel_id"]

    # user_b send a message in his own channel
    message_id_b = requests.post(
        url + "message/send",
        json={
            "token": user_b["token"],
            "channel_id": public_channel_id_b,
            "message": "Nice to see you mate",
        },
    ).json()["message_id"]
    # user_a trying to react the message outside user_a's channel
    response = requests.post(
        url + "message/react",
        json={
            "token": user_a["token"],
            "message_id": message_id_b,
            "react_id": 1,
        },
    )

    # user_a should not be able to react the the message in the public_channel_b
    assert response.status_code == 400


def test_react_invalid_message_id_in_channel(url):
    """
    Test user trying to unreact to a invalid message id
    """
    requests.delete(url + "clear")
    user_a = http_register_n_users(url, 1)
    requests.post(
        url + "channels/create",
        json={"token": user_a["token"], "name": "channel_a", "is_public": True},
    ).json()["channel_id"]
    invalid_message_id = -1
    response = requests.post(
        url + "message/react",
        json={
            "token": user_a["token"],
            "message_id": invalid_message_id,
            "react_id": 1,
        },
    )
    assert response.status_code == 400


def test_react_invalid_message_id_out_channel(url):
    requests.delete(url + "clear")
    user_a, user_b = http_register_n_users(url, 2)
    # user_b create a channel and send message in his own channel
    public_channel_id_b = requests.post(
        url + "channels/create",
        json={"token": user_b["token"], "name": "public_channel_b", "is_public": True},
    ).json()["channel_id"]

    message_id_b = requests.post(
        url + "message/send",
        json={
            "token": user_b["token"],
            "channel_id": public_channel_id_b,
            "message": "Nice to see you mate",
        },
    ).json()["message_id"]

    # user_a trying to reponse in outside the channel
    response = requests.post(
        url + "message/react",
        json={
            "token": user_a["token"],
            "message_id": message_id_b,
            "react_id": 1,
        },
    )
    # user_a should not be able to react the the message in the public_channel_b
    assert response.status_code == 400


def test_react_invalid_react_id(url):
    requests.delete(url + "clear")
    user_a = http_register_n_users(url, 1)

    # user_a create a channel
    public_channel_id = requests.post(
        url + "channels/create",
        json={"token": user_a["token"], "name": "public_channel", "is_public": True},
    ).json()["channel_id"]

    # user_a send a message
    message_id = requests.post(
        url + "message/send",
        json={
            "token": user_a["token"],
            "channel_id": public_channel_id,
            "message": "How are you",
        },
    ).json()["message_id"]
    invalid_react_number = -1

    # user_a react the the message using a invalid message_id
    response = requests.post(
        url + "message/react",
        json={
            "token": user_a["token"],
            "message_id": message_id,
            "react_id": invalid_react_number,
        },
    )
    assert response.status_code == 400


def test_react_duplicate_react(url):
    requests.delete(url + "clear")
    user_a = http_register_n_users(url, 1)

    # user_a create a channel
    public_channel_id = requests.post(
        url + "channels/create",
        json={"token": user_a["token"], "name": "public_channel", "is_public": True},
    ).json()["channel_id"]

    message_id = requests.post(
        url + "message/send",
        json={
            "token": user_a["token"],
            "channel_id": public_channel_id,
            "message": "How are you",
        },
    ).json()["message_id"]

    # React for the first time
    response = requests.post(
        url + "message/react",
        json={
            "token": user_a["token"],
            "message_id": message_id,
            "react_id": 1,
        },
    )
    assert response.status_code == 200

    # React to the same message twice
    response = requests.post(
        url + "message/react",
        json={
            "token": user_a["token"],
            "message_id": message_id,
            "react_id": 1,
        },
    )
    assert response.status_code == 400
