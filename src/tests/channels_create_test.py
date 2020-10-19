import requests
from test_helpers import url, http_register_n_users


def test_http_channels_create_empty_name(url):
    """Testing empty names because the http stack might remove them
    automatically or something. It's clearly an edge case"""
    usera = http_register_n_users(url, 1)

    response = requests.post(
        url + "channels/create",
        json={
            "token": usera["token"],
            "name": "",
            "is_public": True,
        },
    )
    assert response.status_code == 200

    channel_id = response.json()["channel_id"]

    response = requests.get(
        url + "channel/details",
        params={
            "token": usera["token"],
            "channel_id": channel_id,
        },
    )
    assert response.status_code == 200
    channel_details = response.json()
    # empty names are replaced with the name 'new_channel'
    assert channel_details["name"] == "new_channel"
