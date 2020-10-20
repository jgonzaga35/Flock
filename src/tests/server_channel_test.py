import requests
from test_helpers import url, http_register_n_users


###########################################################################
#                       Tests for channels/list                           #
###########################################################################
def test_channels_list_successful(url):
    requests.delete(url + "clear")
    user = http_register_n_users(1)
    channel = requests.post(url + "channels/create", json={
        "token": user["token"],
        "name": "channel_01",
        "is_public": True
    }).json()

    response = requests.get(
        url + "channels/list", params={"token": user["token"]}
    )

    assert response.status_code == 200