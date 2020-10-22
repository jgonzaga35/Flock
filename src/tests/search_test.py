import requests
from channels import channels_create
from channel import channel_join, channel_addowner, channel_removeowner, channel_invite
from message import message_send
from other import search, clear
from test_helpers import url, register_n_users


def test_search_one_channel_three_users():
    clear()

    usera, userb, userc = register_n_users(3)

    channel_id = channels_create(usera["token"], "channel of A", is_public=True)[
        "channel_id"
    ]

    message_send(usera["token"], channel_id, "Hello message #match")

    channel_join(userb["token"], channel_id)

    message_send(usera["token"], channel_id, "Hello userb!")
    message_send(userb["token"], channel_id, "Hello owner #match")

    channel_join(userc["token"], channel_id)
    message_send(userc["token"], channel_id, "Yo everyone #match")

    message_send(usera["token"], channel_id, "So many people")

    matching = search(usera["token"], "#match")

    # all the users are part of the same channel, so they see the same messages
    assert matching == search(userb["token"], "#match")
    assert matching == search(userc["token"], "#match")

    for i, message in enumerate(
        [
            {"author": userc["u_id"], "content": "Yo everyone #match"},
            {"author": userb["u_id"], "content": "Hello owner #match"},
            {"author": usera["u_id"], "content": "Hello message #match"},
        ]
    ):
        assert matching["messages"][i]["message"] == message["content"]
        assert matching["messages"][i]["u_id"] == message["author"]


def test_search_three_channels_five_users():
    clear()

    usera, userb, userc, userd, usere = register_n_users(5)

    channel_a_id = channels_create(usera["token"], "channel of A", is_public=True)[
        "channel_id"
    ]

    id1 = message_send(usera["token"], channel_a_id, "welcome to my channel #match")[
        "message_id"
    ]

    # user b joins channel A
    channel_join(userb["token"], channel_a_id)
    message_send(userb["token"], channel_a_id, "hello owner A!")["message_id"]

    # user D and E have a channel together
    channel_de_id = channels_create(
        userd["token"], "channel of d and e", is_public=False
    )["channel_id"]
    channel_addowner(userd["token"], channel_de_id, usere["u_id"])
    id3 = message_send(userd["token"], channel_de_id, "our own channel! #match")[
        "message_id"
    ]
    message_send(usere["token"], channel_de_id, "how cool!")["message_id"]

    # userc becomes the only owner of channel A
    channel_addowner(usera["token"], channel_a_id, userc["u_id"])
    id5 = message_send(usera["token"], channel_a_id, "everyone meet C #match")[
        "message_id"
    ]
    channel_removeowner(usera["token"], channel_a_id, usera["u_id"])

    # user B invites D to the channel of A
    id6 = message_send(
        userb["token"], channel_a_id, "I'm gonna invite someone, get ready! #match"
    )["message_id"]
    channel_invite(userb["token"], channel_a_id, userd["u_id"])
    message_send(
        userd["token"],
        channel_a_id,
        "Hello everyone! Cheers for the invite.",
    )["message_id"]

    # user b creates a new channel with everyone
    channel_b_id = channels_create(userb["token"], "everyone!", is_public=True)[
        "channel_id"
    ]
    channel_invite(userb["token"], channel_b_id, usera["u_id"])
    channel_invite(userb["token"], channel_b_id, userc["u_id"])
    id8 = message_send(
        userc["token"], channel_b_id, "a message that everyone will see #match"
    )["message_id"]
    channel_invite(userb["token"], channel_b_id, userd["u_id"])
    channel_invite(userb["token"], channel_b_id, usere["u_id"])

    id9 = message_send(
        usere["token"],
        channel_de_id,
        "yo did you see the channel with everyone? #match",
    )["message_id"]

    # usera sees all the message in channel a, even though is not an owner anymore
    results = search(usera["token"], "#match")
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
    assert results == search(userb["token"], "#match")
    # same for user C (even if C is the owner of the channel now)
    assert results == search(userc["token"], "#match")

    results = search(userd["token"], "#match")
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
    results = search(usere["token"], "#match")
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


def test_search_no_match():
    clear()

    user = register_n_users(1)
    channel_id = channels_create(user["token"], "channel", is_public=True)["channel_id"]
    message_send(user["token"], channel_id, "hello world")
    message_send(user["token"], channel_id, "this is a test")
    message_send(user["token"], channel_id, "no words contain the keyword")
    message_send(user["token"], channel_id, "but what is the key word going to be")
    message_send(user["token"], channel_id, "lorem ipsum?")
    message_send(user["token"], channel_id, "not anymore")

    assert len(search(user["token"], "search")["messages"]) == 0
