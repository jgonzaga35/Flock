import requests
from test_helpers import url, http_register_n_users


def test_messages_unreact_successfully(url):
    requests.delete(url + "clear")
    user_a, user_b = http_register_n_users(url, 2)
    # user_a create a public channel
    channel_a_id = requests.post(
        url + "channels/create",
        json={"token": user_a["token"], "name": "channel_a", "is_public": True},
    ).json()["channel_id"]

    requests.post(
        url + "channel/join",
        json={"token": user_b["token"], "channel_id": channel_a_id},
    )

    message_id = requests.post(
        url + "message/send",
        json={
            "token": user_b["token"],
            "channel_id": channel_a_id,
            "message": "Hi",
        },
    ).json()["message_id"]
    response = requests.post(
        url + "message/react",
        json={
            "token": user_a["token"],
            "message_id": message_id,
            "react_id": 1,
        },
    )
    assert response.status_code == 200

    # User_a has reacted to the channel
    message = requests.get(
        url + "channel/messages",
        params={
            "token": user_a["token"],
            "channel_id": channel_a_id,
            "start": 0,
        },
    ).json()["messages"][0]
    assert message["reacts"][0]["is_this_user_reacted"] == True

    # User_a has unreacted to the channel
    response = requests.post(
        url + "message/unreact",
        json={
            "token": user_a["token"],
            "message_id": message_id,
            "react_id": 1,
        },
    )
    assert response.status_code == 200

    message = requests.get(
        url + "channel/messages",
        params={
            "token": user_a["token"],
            "channel_id": channel_a_id,
            "start": 0,
        },
    ).json()["messages"][0]
    # User_a is not react for now
    assert message["reacts"][0]["is_this_user_reacted"] == False


def test_unreact_invalid_message_id(url):
    """
    Test user trying to unreact to a invalid message id
    """
    requests.delete(url + "clear")
    user_a = http_register_n_users(url, 1)
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


def test_unreact_invalid_react_id(url):
    requests.delete(url + "clear")
    user_a = http_register_n_users(url, 1)
    public_channel_id = requests.post(
        url + "channels/create",
        json={"token": user_a["token"], "name": "public_channel", "is_public": True},
    ).json()["channel_id"]

    message_id = requests.post(
        url + "message/send",
        json={
            "token": user_a["token"],
            "channel_id": public_channel_id,
            "message": "Nice to see you mate",
        },
    ).json()["message_id"]
    response = requests.post(
        url + "message/react",
        json={
            "token": user_a["token"],
            "message_id": message_id,
            "react_id": 1,
        },
    )
    assert response.status_code == 200

    invalid_react_number = -1
    response = requests.post(
        url + "message/unreact",
        json={
            "token": user_a["token"],
            "message_id": message_id,
            "react_id": invalid_react_number,
        },
    )

    assert response.status_code == 400


def test_unreact_inactive_react_id(url):
    """
    situation where a user trying to unreact a message which haven't been reacted
    """
    requests.delete(url + "clear")
    user_a = http_register_n_users(url, 1)
    public_channel_id = requests.post(
        url + "channels/create",
        json={"token": user_a["token"], "name": "public_channel", "is_public": True},
    ).json()["channel_id"]

    message_id = requests.post(
        url + "message/send",
        json={
            "token": user_a["token"],
            "channel_id": public_channel_id,
            "message": "Nice to see you mate",
        },
    ).json()["message_id"]

    # React id 1 is a valid id but not active
    response = requests.post(
        url + "message/unreact",
        json={
            "token": user_a["token"],
            "message_id": message_id,
            "react_id": 1,
        },
    )
    assert response.status_code == 400
