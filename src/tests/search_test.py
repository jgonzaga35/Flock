import requests
from database import clear_database
from channels import channels_create
from channel import channel_join
from message import message_send
from other import search
from test_helpers import url, register_n_users


def test_search_one_channel_three_users():
    clear_database()

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

    matching_messages = search(usera["token"], "#match")

    # all the users are part of the same channel, so they see the same messages
    assert matching_messages == search(userb["token"], "#match")
    assert matching_messages == search(userc["token"], "#match")

    for i, message in enumerate(
        [
            {"author": userc["u_id"], "content": "Yo everyone #match"},
            {"author": userb["u_id"], "content": "Hello owner #match"},
            {"author": usera["u_id"], "content": "Hello message #match"},
        ]
    ):
        assert matching_messages[i]["message"] == message["content"]
        assert matching_messages[i]["u_id"] == message["author"]
