import requests
from test_helpers import url, http_register_n_users


def test_search_one_channel_three_users(url):
    requests.delete(url + "clear")

    usera, userb, userc = http_register_n_users(url, 3)

    channel_id = requests.post(
        url + "channels/create",
        json={"token": usera["token"], "name": "channel of A", "is_public": True},
    ).json()["channel_id"]

    requests.post(
        url + "message/send",
        json={
            "token": usera["token"],
            "channel_id": channel_id,
            "message": "Hello message #match",
        },
    )

    requests.post(
        url + "channel/join",
        json={"token": userb["token"], "channel_id": channel_id},
    )

    requests.post(
        url + "message/send",
        json={
            "token": usera["token"],
            "channel_id": channel_id,
            "message": "Hello userb!",
        },
    )

    requests.post(
        url + "message/send",
        json={
            "token": userb["token"],
            "channel_id": channel_id,
            "message": "Hello owner #match",
        },
    )

    requests.post(
        url + "channel/join",
        json={"token": userc["token"], "channel_id": channel_id},
    )
    requests.post(
        url + "message/send",
        json={
            "token": userc["token"],
            "channel_id": channel_id,
            "message": "Yo everyone #match",
        },
    )

    requests.post(
        url + "message/send",
        json={
            "token": usera["token"],
            "channel_id": channel_id,
            "message": "So many people",
        },
    )
    matching = requests.get(
        url + "/search", params={"token": usera["token"], "query_str": "#match"}
    ).json()

    # all the users are part of the same channel, so they see the same messages
    assert (
        matching
        == requests.get(
            url + "/search", params={"token": userb["token"], "query_str": "#match"}
        ).json()
    )
    assert (
        matching
        == requests.get(
            url + "/search", params={"token": userc["token"], "query_str": "#match"}
        ).json()
    )

    for i, message in enumerate(
        [
            {"author": userc["u_id"], "content": "Yo everyone #match"},
            {"author": userb["u_id"], "content": "Hello owner #match"},
            {"author": usera["u_id"], "content": "Hello message #match"},
        ]
    ):
        assert matching["messages"][i]["message"] == message["content"]
        assert matching["messages"][i]["u_id"] == message["author"]


def test_search_three_channels_five_users(url):

    requests.delete(url + "clear")
    usera, userb, userc, userd, usere = http_register_n_users(url, 5)

    channel_a_id = requests.post(
        url + "channels/create",
        json={"token": usera["token"], "name": "channel of A", "is_public": True},
    ).json()["channel_id"]

    id1 = requests.post(
        url + "message/send",
        json={
            "token": usera["token"],
            "channel_id": channel_a_id,
            "message": "welcome to my channel #match",
        },
    ).json()["message_id"]

    # user b joins channel A
    requests.post(
        url + "channel/join",
        json={"token": userb["token"], "channel_id": channel_a_id},
    )

    requests.post(
        url + "message/send",
        json={
            "token": userb["token"],
            "channel_id": channel_a_id,
            "message": "hello owner A!",
        },
    )

    # user D and E have a channel together
    channel_de_id = requests.post(
        url + "channels/create",
        json={
            "token": userd["token"],
            "name": "channel of d and e",
            "is_public": False,
        },
    ).json()["channel_id"]

    requests.post(
        url + "channel/addowner",
        json={
            "token": userd["token"],
            "channel_id": channel_de_id,
            "u_id": usere["u_id"],
        },
    )

    id3 = requests.post(
        url + "message/send",
        json={
            "token": userd["token"],
            "channel_id": channel_de_id,
            "message": "our own channel! #match",
        },
    ).json()["message_id"]
    requests.post(
        url + "message/send",
        json={
            "token": usere["token"],
            "channel_id": channel_de_id,
            "message": "how cool!",
        },
    )

    # userc becomes the only owner of channel A
    requests.post(
        url + "channel/addowner",
        json={
            "token": usera["token"],
            "channel_id": channel_a_id,
            "u_id": userc["u_id"],
        },
    )
    id5 = requests.post(
        url + "message/send",
        json={
            "token": usera["token"],
            "channel_id": channel_a_id,
            "message": "everyone meet C #match",
        },
    ).json()["message_id"]

    requests.post(
        url + "channel/removeowner",
        json={
            "token": usera["token"],
            "channel_id": channel_a_id,
            "u_id": usera["u_id"],
        },
    )

    # user B invites D to the channel of A
    id6 = requests.post(
        url + "message/send",
        json={
            "token": userb["token"],
            "channel_id": channel_a_id,
            "message": "I'm gonna invite someone, get ready! #match",
        },
    ).json()["message_id"]

    requests.post(
        url + "channel/invite",
        json={
            "token": userb["token"],
            "channel_id": channel_a_id,
            "u_id": userd["u_id"],
        },
    )
    requests.post(
        url + "message/send",
        json={
            "token": userd["token"],
            "channel_id": channel_a_id,
            "message": "Hello everyone! Cheers for the invite.",
        },
    )

    # user b creates a new channel with everyone
    channel_b_id = requests.post(
        url + "channels/create",
        json={"token": userb["token"], "name": "everyone!", "is_public": True},
    ).json()["channel_id"]

    requests.post(
        url + "channel/invite",
        json={
            "token": userb["token"],
            "channel_id": channel_b_id,
            "u_id": usera["u_id"],
        },
    )
    requests.post(
        url + "channel/invite",
        json={
            "token": userb["token"],
            "channel_id": channel_b_id,
            "u_id": userc["u_id"],
        },
    )
    id8 = requests.post(
        url + "message/send",
        json={
            "token": userc["token"],
            "channel_id": channel_b_id,
            "message": "a message that everyone will see #match",
        },
    ).json()["message_id"]

    requests.post(
        url + "channel/invite",
        json={
            "token": userb["token"],
            "channel_id": channel_b_id,
            "u_id": userd["u_id"],
        },
    )
    requests.post(
        url + "channel/invite",
        json={
            "token": userb["token"],
            "channel_id": channel_b_id,
            "u_id": usere["u_id"],
        },
    )
    id9 = requests.post(
        url + "message/send",
        json={
            "token": usere["token"],
            "channel_id": channel_de_id,
            "message": "yo did you see the channel with everyone? #match",
        },
    ).json()["message_id"]

    # usera sees all the message in channel a, even though is not an owner anymore
    results = requests.get(
        url + "/search", params={"token": usera["token"], "query_str": "#match"}
    ).json()
    for i, message in enumerate(
        [
            {
                "author": userc["u_id"],
                "content": "a message that everyone will see #match",
                "id": id8,
            },
            {
                "author": userb["u_id"],
                "content": "I'm gonna invite someone, get ready! #match",
                "id": id6,
            },
            {
                "author": usera["u_id"],
                "content": "everyone meet C #match",
                "id": id5,
            },
            {
                "author": usera["u_id"],
                "content": "welcome to my channel #match",
                "id": id1,
            },
        ]
    ):
        assert results["messages"][i]["u_id"] == message["author"]
        assert results["messages"][i]["message"] == message["content"]
        assert results["messages"][i]["message_id"] == message["id"]

    # user B sees the same messages because he is in the same channels as a
    assert (
        results
        == requests.get(
            url + "/search", params={"token": userb["token"], "query_str": "#match"}
        ).json()
    )
    # same for user C (even if C is the owner of the channel now)
    assert (
        results
        == requests.get(
            url + "/search", params={"token": userc["token"], "query_str": "#match"}
        ).json()
    )

    results == requests.get(
        url + "/search", params={"token": userd["token"], "query_str": "#match"}
    ).json()
    for i, message in enumerate(
        [
            {
                "author": usere["u_id"],
                "content": "yo did you see the channel with everyone? #match",
                "id": id9,
            },
            {
                "author": userc["u_id"],
                "content": "a message that everyone will see #match",
                "id": id8,
            },
            {
                "author": userb["u_id"],
                "content": "I'm gonna invite someone, get ready! #match",
                "id": id6,
            },
            {
                "author": usera["u_id"],
                "content": "everyone meet C #match",
                "id": id5,
            },
            {
                "author": userd["u_id"],
                "content": "our own channel! #match",
                "id": id3,
            },
            {
                "author": usera["u_id"],
                "content": "welcome to my channel #match",
                "id": id1,
            },
        ]
    ):
        assert results["messages"][i]["u_id"] == message["author"]
        assert results["messages"][i]["message"] == message["content"]
        assert results["messages"][i]["message_id"] == message["id"]

    # user E only sees the messages in channel DE and the third channel
    results = requests.get(
        url + "/search", params={"token": usere["token"], "query_str": "#match"}
    ).json()
    for i, message in enumerate(
        [
            {
                "author": usere["u_id"],
                "content": "yo did you see the channel with everyone? #match",
                "id": id9,
            },
            {
                "author": userc["u_id"],
                "content": "a message that everyone will see #match",
                "id": id8,
            },
            {
                "author": userd["u_id"],
                "content": "our own channel! #match",
                "id": id3,
            },
        ]
    ):
        assert results["messages"][i]["u_id"] == message["author"]
        assert results["messages"][i]["message"] == message["content"]
        assert results["messages"][i]["message_id"] == message["id"]

