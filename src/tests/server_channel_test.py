import requests
from test_helpers import url, http_register_n_users


###########################################################################
#                       Tests for channels/list                           #
###########################################################################
# User part of one channel
def test_channels_list_successful(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    channel = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_01", "is_public": True},
    ).json()

    response = requests.get(url + "channels/list", params={"token": user["token"]})
    assert response.status_code == 200
    channels_list = response.json()
    assert channel["channel_id"] in [x["channel_id"] for x in channels_list]


# User part of two chanels
