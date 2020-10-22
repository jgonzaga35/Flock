import requests
from test_helpers import url, http_register_n_users

def test_messages_no_messages(url):
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