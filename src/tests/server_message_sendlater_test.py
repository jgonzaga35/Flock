import time
import requests
import pytest
from test_helpers import http_register_n_users, url

DELAY_SCALE = 1


def test_message_sendlater_succcessful_web(url):
    assert requests.delete(url + "clear").status_code == 200

    user = http_register_n_users(url, 1)

    channel_id = requests.post(
        url + "channels/create",
        json={
            "token": user["token"],
            "name": "channel_name",
            "is_public": True,
        },
    ).json()["channel_id"]

    send_at = int(round(time.time() + 2 * DELAY_SCALE))
    assert (
        requests.post(
            url + "message/sendlater",
            json={
                "token": user["token"],
                "channel_id": channel_id,
                "message": "hello",
                "time_sent": send_at,
            },
        ).status_code
        == 200
    )

    time.sleep(2 * DELAY_SCALE + 1 * DELAY_SCALE)

    messages = requests.get(
        url + "channel/messages",
        params={
            "token": user["token"],
            "channel_id": channel_id,
            "start": 0,
        },
    ).json()["messages"]

    assert len(messages) == 1
    assert messages[0]["message"] == "hello"


def test_message_sendlater_4xx_web(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    channel_id = requests.post(
        url + "channels/create",
        json={
            "token": user["token"],
            "name": "channel_name",
            "is_public": True,
        },
    ).json()["channel_id"]

    assert (
        requests.post(
            url + "message/sendlater",
            json={
                "token": -1,
                "channel_id": channel_id,
                "message": "message",
                "time_sent": int(round(time.time() + 2)),
            },
        ).status_code
        == 403
    )

    assert (
        requests.post(
            url + "message/sendlater",
            json={
                "token": user["token"],
                "channel_id": -1,
                "message": "asdfasfd",
                "time_sent": int(round(time.time() + 2)),
            },
        ).status_code
        == 400
    )
