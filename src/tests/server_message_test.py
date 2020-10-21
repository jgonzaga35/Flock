import requests
from test_helpers import url, http_register_n_users

##############################################################
#                   Tests for message/send                   #
##############################################################

def test_send_one_message(url):
    pass
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    # Create a channel
    response = requests.post(
        url + "channels/create", 
        json={
            "token": user["token"],
            "name": "channel_01",
            "is_public": True
        }    
    )
    assert response.status_code == 200
    channel = response.json()

    # Send a message
    message = requests.post(
        url + "message/send",
        json={
            "token": user["token"],
            "channel": channel["channel_id"],
            "message": "test message"
        }
    )
    assert message.status_code() == 200

    # Get a list of messages in the channel
    response = requests.get(
        url + "channel/messages",
        params={
            "token": user["token"],
            "channel_id": channel["channel_id"],
            "start": 0
        }
    )
    assert response.status_code == 200
    
    # Ensure message in the channel
    channel_messages = response.json()
    assert "test message" in [x["message"] for x in channel_messages]