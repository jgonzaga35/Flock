import requests
from test_helpers import http_register_n_users, url


def test_http_channel_details_valid(url):
    requests.delete(url + "clear")
    usera = http_register_n_users(url, 1)
    response = requests.post(
        url + "channels/create",
        json={
            "token": usera["token"],
            "name": "channel of A",
            "is_public": False,
        },
    )
    assert response.status_code == 200
    channel_id = response.json()["channel_id"]

    response = requests.get(
        url + "channel/details",
        params={"token": usera["token"], "channel_id": channel_id},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "channel of A"
