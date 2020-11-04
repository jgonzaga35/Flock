from test_helpers import url, http_register_n_users
from error import AccessError, InputError
import pytest
import requests

@pytest.fixture
def create_channel(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    # Create a channel
    channel_params = {
        "token": user["token"],
        "name": "channel_01",
        "is_public": True,
    }
    response = requests.post(url + "channels/create", json=channel_params)
    assert response.status_code == 200
    channel = response.json()

    # User sends a message
    message_params = {
        "token": user["token"],
        "channel_id": channel["channel_id"],
        "message": "test message",
    }
    response = requests.post(url + "message/send", json=message_params)
    assert response.status_code == 200
    message = response.json()

    return [url, user, channel, message]

def test_message_pin_public_simple(create_channel):
    url, user, channel, message = create_channel 

    # Return messages in channel
    channel_msg_params= {
        "token": user["token"],
        "channel_id": channel["channel_id"],
        "start": 0,
    }

    # Return messages in channel
    response = requests.get(url + "channel/messages", params=channel_msg_params)
    assert response.status_code == 200
    channel_msg = response.json()

    # Ensure message is not pinned
    assert channel_msg["messages"][0]["is_pinned"] == False
    
    response = requests.post(
        url + "message/pin",
        params={
            "token": user["token"],
            "message_id": message["message_id"],
        }
    )
    assert response.status_code == 200
    assert channel_msg["messages"][0]["is_pinned"] == False