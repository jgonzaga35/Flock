from channel import (
    channel_messages,
    channel_invite,
    channel_leave,
    channel_addowner,
    channel_join,
    channel_details,
    formated_user_details_from_user_data,
    channel_removeowner,
)
from message import message_send
from auth import auth_get_user_data_from_id
from channels import channels_create, channels_list
from database import clear_database
from error import InputError, AccessError
from word_list import word_list
import time
import random
import pytest
from test_helpers import register_n_users

#################################################################################
#                       Tests for channel_messages
#################################################################################
def test_messages_no_messages():
    clear_database()
    user = register_n_users(1)
    channel = channels_create(user["token"], "channel", is_public=True)
    messages_in_channel = channel_messages(
        user["token"], channel["channel_id"], start=0
    )

    assert len(messages_in_channel["messages"]) == 0
    assert messages_in_channel["start"] == 0
    assert messages_in_channel["end"] == -1


def test_messages_invalid_channel_ID():
    clear_database()
    user = register_n_users(1)
    invalid_channel_id = -1
    with pytest.raises(InputError):
        assert channel_messages(user["token"], invalid_channel_id, 0)


def test_channel_messages_invalid_start():
    clear_database()
    user = register_n_users(1)

    channel_id = channels_create(user["token"], "channel", is_public=True)["channel_id"]

    with pytest.raises(InputError):
        assert channel_messages(user["token"], channel_id, start=-1)

    with pytest.raises(InputError):
        assert channel_messages(user["token"], channel_id, start=1)


def test_messages_user_not_member():
    clear_database()

    user_01, user_02 = register_n_users(2)
    channel = channels_create(user_01["token"], "channel_01", is_public=True)
    channel_join(user_01["token"], channel["channel_id"])

    with pytest.raises(AccessError):
        assert channel_messages(user_02["token"], channel["channel_id"], 0)


def test_messages_invalid_token():
    clear_database()
    with pytest.raises(AccessError):
        channel_messages(-1, 0, 0)


# ----------------------------- Add these tests when message_send is implemented ------------------
def test_messages_negative_start_index():
    clear_database()
    # Add a user and log them in
    user = register_n_users(1)

    # Create a channel and fill with messages
    channel = channels_create(user["token"], "new_channel", is_public=True)
    populate_channel_hundred_messages(user["token"], channel["channel_id"])
    with pytest.raises(InputError):
        assert channel_messages(user["token"], channel["channel_id"], -1)


def test_messages_simple():
    clear_database()
    # Add a user and log them in
    user = register_n_users(1)

    # Create a channel and fill with messages
    channel = channels_create(user["token"], "new_channel", is_public=True)
    message_send(user["token"], channel["channel_id"], "Hello World!")
    res = channel_messages(user["token"], channel["channel_id"], 0)
    assert res["messages"][0]["message"] == "Hello World!"


def test_messages_start_overflow():
    clear_database()
    user = register_n_users(1)
    channel = channels_create(user["token"], "channel_01", is_public=True)
    channel_join(user["token"], channel["channel_id"])
    message_send(user["token"], channel["channel_id"], "Hello World!")
    with pytest.raises(InputError):
        assert channel_messages(user["token"], channel["channel_id"], 100)


def test_messages_start_underflow():
    clear_database()
    user = register_n_users(1)

    channel = channels_create(user["token"], "channel_01", is_public=True)
    channel_join(user["token"], channel["channel_id"])
    message_send(user["token"], channel["channel_id"], "Hello World!")
    assert channel_messages(user["token"], channel["channel_id"], 0)["end"] == -1


def test_channel_message_a_lot_of_message():
    """
    This test uses randomness. That means that running this test twice will
    not do the exact same thing, so sometimes it might fail, sometimes not.

    If it does, then pytest will print out the seed. Copy it, and then give it
    to random.seed (below). Like this, the random module will always generate
    the same sequence of random number, and you can debug the failing test case.
    """
    seed = time.time()
    print("seed", seed)
    random.seed(seed)

    clear_database()
    usera, userb, userc = register_n_users(3)
    channel_id = channels_create(usera["token"], "channel", is_public=True)[
        "channel_id"
    ]

    channel_join(userb["token"], channel_id)
    channel_join(userc["token"], channel_id)

    # generate random messages
    for _ in range(340):
        token = random.choice([usera, userb, userc])["token"]
        word = random.choice(word_list)
        message_send(token, channel_id, word)

    # make sure that usera, userb and userc all get the same messages
    assert channel_messages(userb["token"], channel_id, 5) == channel_messages(
        userc["token"], channel_id, 5
    )
    assert channel_messages(userb["token"], channel_id, 5) == channel_messages(
        usera["token"], channel_id, 5
    )

    # makes sure all of the message are sorted by date (newer first)
    #    messages[0] should be newer than messages[1]
    #    => messages[0]['time_created'] > messages[1]['time_created']
    messages = channel_messages(userc["token"], channel_id, random.randint(0, 340))[
        "messages"
    ]
    prev_msg_time = None
    for message in messages:
        if prev_msg_time is None:
            prev_msg_time = message["time_created"]
        else:
            assert prev_msg_time >= message["time_created"]
            prev_msg_time = message["time_created"]

    # makes sure that start and end make sense when we can load 50 messages
    assert channel_messages(userb["token"], channel_id, 5)["start"] == 5
    assert channel_messages(userb["token"], channel_id, 5)["end"] == 55

    # make sure that start and end make sense when we can't load 50 messages
    assert channel_messages(userb["token"], channel_id, 330)["start"] == 330
    assert channel_messages(userb["token"], channel_id, 330)["end"] == -1


# Helper function to send 100 messages to a given channel
def populate_channel_hundred_messages(token, channel_id):
    for _ in range(1, 100):
        index = random.randint(0, len(word_list) - 1)
        message = word_list[index]
        message_send(token, channel_id, message)


# ---------------------------------------------------------------------------------------------


def test_join_invalid_token():
    clear_database()
    with pytest.raises(AccessError):
        channel_join(-1, 0)


def test_channel_join_multiple_channels():
    clear_database()
    usera, userb, userc = register_n_users(3)
    channel_id_a = channels_create(usera["token"], "channela", is_public=True)[
        "channel_id"
    ]
    channel_id_b = channels_create(userb["token"], "channelb", is_public=True)[
        "channel_id"
    ]
    channel_id_c = channels_create(userc["token"], "channelc", is_public=True)[
        "channel_id"
    ]

    channel_join(usera["token"], channel_id_b)
    channel_join(usera["token"], channel_id_c)
    channel_join(userb["token"], channel_id_c)

    # usera should be able to get all the details since the channels are public
    detailsa = channel_details(usera["token"], channel_id_a)
    detailsb = channel_details(usera["token"], channel_id_b)
    detailsc = channel_details(usera["token"], channel_id_c)

    # there should still be only one owner
    assert_contains_users_id(detailsa["owner_members"], [usera["u_id"]])
    assert_contains_users_id(detailsb["owner_members"], [userb["u_id"]])
    assert_contains_users_id(detailsc["owner_members"], [userc["u_id"]])

    assert_contains_users_id(detailsa["all_members"], [usera["u_id"]])
    assert_contains_users_id(detailsb["all_members"], [usera["u_id"], userb["u_id"]])
    assert_contains_users_id(
        detailsc["all_members"], [usera["u_id"], userb["u_id"], userc["u_id"]]
    )


# Join the channel successfully
def test_join_channel_successfully():
    clear_database()
    user_A, user_B = register_n_users(2)
    public_channel = channels_create(user_A["token"], "Channel_A", True)
    channel_join(user_B["token"], public_channel["channel_id"])
    details = channel_details(user_A["token"], public_channel["channel_id"])
    expected_member_ids = [user_A["u_id"], user_B["u_id"]]

    assert_contains_users_id(details["all_members"], expected_member_ids)


# user try to join a channel with invalid channel id
def test_join_channel_with_invalid_channel_id():
    clear_database()
    user = register_n_users(1)
    invalid_channel_id = 233

    with pytest.raises(InputError):
        channel_join(user["token"], invalid_channel_id)


# join a user without authority to a channel
def test_join_channel_without_authority():
    clear_database()
    user_A, user_B = register_n_users(2)
    channel = channels_create(
        user_A["token"], "Private_channel", False
    )  # Create a new private channel

    with pytest.raises(AccessError):
        channel_join(user_B["token"], channel["channel_id"])


def test_leave_invalid_token():
    clear_database()
    with pytest.raises(AccessError):
        channel_leave(-1, 0)


# user successfully leave the channel
def test_leave_channel_successfully():
    clear_database()
    user_A, user_B = register_n_users(2)
    public_channel = channels_create(
        user_A["token"], "public_channel", True
    )  # Create public channel

    # user_B join the channel, we have two users in the channel now
    channel_join(user_B["token"], public_channel["channel_id"])
    details = channel_details(user_A["token"], public_channel["channel_id"])
    expected_members_id = [user_A["u_id"], user_B["u_id"]]
    assert_contains_users_id(details["all_members"], expected_members_id)

    # user_B leave the channel, only user_A left in the channel
    channel_leave(user_B["token"], public_channel["channel_id"])
    details = channel_details(user_A["token"], public_channel["channel_id"])
    expected_members_id = [user_A["u_id"]]
    assert_contains_users_id(details["all_members"], expected_members_id)


def test_inexist_uesr_leave_channel_private():
    clear_database()
    user_A, user_B = register_n_users(2)
    private_channel = channels_create(
        user_A["token"], "private_channel", False
    )  # a private channel

    with pytest.raises(AccessError):
        channel_leave(user_B["token"], private_channel["channel_id"])


def test_inexist_uesr_leave_channel_public():
    clear_database()
    user_A, user_B = register_n_users(2)
    public_channel = channels_create(
        user_A["token"], "public_channel", True
    )  # User A create a public channel and

    with pytest.raises(AccessError):
        channel_leave(user_B["token"], public_channel["channel_id"])


def test_leave_channel_id_invalid():
    clear_database()
    user = register_n_users(1)
    channel_id = channels_create(user["token"], "channel_A", True)["channel_id"]
    invalid_channel_id = channel_id + 1

    with pytest.raises(InputError):
        channel_leave(user["token"], invalid_channel_id)


def test_channel_details_invalid_token():
    clear_database()
    with pytest.raises(AccessError):
        channel_details(-1, 0)


def test_channel_details_basic():
    clear_database()

    usera = register_n_users(1)

    channel_id = channels_create(usera["token"], "channel1", True)["channel_id"]

    details1 = channel_details(usera["token"], channel_id)
    assert details1 == {
        "name": "channel1",
        "owner_members": [
            formated_user_details_from_user_data(
                auth_get_user_data_from_id(usera["u_id"])
            )
        ],
        "all_members": [
            formated_user_details_from_user_data(
                auth_get_user_data_from_id(usera["u_id"])
            )
        ],
    }


def test_channel_details_private():
    clear_database()

    usera, userb = register_n_users(2)

    channel_id = channels_create(userb["token"], "channel2", False)["channel_id"]

    assert channel_details(userb["token"], channel_id) == {
        "name": "channel2",
        "owner_members": [
            formated_user_details_from_user_data(
                auth_get_user_data_from_id(userb["u_id"])
            )
        ],
        "all_members": [
            formated_user_details_from_user_data(
                auth_get_user_data_from_id(userb["u_id"])
            )
        ],
    }

    with pytest.raises(AccessError):
        channel_details(usera["token"], channel_id)


def test_channel_details_invalid_id():
    clear_database()
    usera, _ = register_n_users(2)
    with pytest.raises(InputError):
        channel_details(usera["token"], 1)


def test_add_owner_invalid_id():
    clear_database()
    usera, userb = register_n_users(2)
    channel_id = channels_create(usera["token"], "channel_name", is_public=True)[
        "channel_id"
    ]
    channel_join(userb["token"], channel_id)

    with pytest.raises(AccessError):
        channel_addowner(-1, channel_id, userb["u_id"])


def test_add_owner_successfully():
    clear_database()
    user_A, user_B = register_n_users(2)
    public_channel = channels_create(user_A["token"], "public_channel", True)
    channel_join(user_B["token"], public_channel["channel_id"])

    # user_A add user_B as onwer, gotta check whether user_B is in owner list
    channel_addowner(user_A["token"], public_channel["channel_id"], user_B["u_id"])
    details = channel_details(user_A["token"], public_channel["channel_id"])
    expect_owner_in_channel = [user_A["u_id"], user_B["u_id"]]
    assert_contains_users_id(details["owner_members"], expect_owner_in_channel)


def test_add_owner_with_invalid_channel_id():
    clear_database()
    user_A, user_B = register_n_users(2)
    public_channel = channels_create(user_A["token"], "public_channel", True)
    channel_join(user_B["token"], public_channel["channel_id"])
    with pytest.raises(InputError):
        invalid_channel_id = 233
        channel_addowner(user_A["token"], invalid_channel_id, user_B["u_id"])


def test_add_owner_repeatedly():
    clear_database()
    user_A, user_B = register_n_users(2)
    public_channel = channels_create(user_A["token"], "public_channel", True)
    channel_join(user_B["token"], public_channel["channel_id"])
    channel_addowner(user_A["token"], public_channel["channel_id"], user_B["u_id"])
    with pytest.raises(InputError):
        channel_addowner(user_A["token"], public_channel["channel_id"], user_B["u_id"])


def test_add_invalid_user_to_owner():
    clear_database()
    user_A = register_n_users(1)
    private_channel = channels_create(user_A["token"], "private_channel", False)
    invalid_uid = 233
    with pytest.raises(InputError):
        channel_addowner(user_A["token"], private_channel["channel_id"], invalid_uid)


# We assume all of the user are in a public channel
# One of them are the owner whereas other two are common user in this channel
def test_add_owner_by_non_owner():
    clear_database()
    user_A, user_B, user_C = register_n_users(3)
    public_channel = channels_create(
        user_A["token"], "public_channel", True
    )  # user_A create the channel and be the owner
    channel_join(
        user_C["token"], public_channel["channel_id"]
    )  # Other two user join in the channel
    channel_join(user_B["token"], public_channel["channel_id"])
    with pytest.raises(AccessError):
        channel_addowner(
            user_B["token"], public_channel["channel_id"], user_C["u_id"]
        )  # user_B who are not owner add common user
        # user_C be the owner


def test_remove_owner_invalid_token():
    clear_database()
    with pytest.raises(AccessError):
        channel_removeowner(-1, 0, 0)


def test_remove_user_successfully():
    clear_database()
    user_A, user_B = register_n_users(2)
    public_channel = channels_create(user_A["token"], "public_channel", True)
    channel_join(user_B["token"], public_channel["channel_id"])

    # Add user_B as owner and check whether user_B is in the owner list
    channel_addowner(user_A["token"], public_channel["channel_id"], user_B["u_id"])
    details = channel_details(user_A["token"], public_channel["channel_id"])
    expect_owner_in_channel = [user_A["u_id"], user_B["u_id"]]
    assert_contains_users_id(details["owner_members"], expect_owner_in_channel)

    # Remove user_B from owner list and check whether user_B has been removed
    channel_removeowner(user_A["token"], public_channel["channel_id"], user_B["u_id"])
    details = channel_details(user_A["token"], public_channel["channel_id"])
    expect_owner_in_channel = [user_A["u_id"]]
    assert_contains_users_id(details["owner_members"], expect_owner_in_channel)


def test_remove_owner_with_invalid_channel_id():
    clear_database()
    user_A, user_B = register_n_users(2)
    public_channel = channels_create(user_A["token"], "public_channel", True)
    channel_join(user_B["token"], public_channel["channel_id"])
    channel_addowner(user_A["token"], public_channel["channel_id"], user_B["u_id"])

    with pytest.raises(InputError):
        invalid_channel_id = 233
        channel_removeowner(user_A["token"], invalid_channel_id, user_B["u_id"])


def test_remove_owner_to_non_owner():
    clear_database()
    user_A, user_B = register_n_users(2)
    public_channel = channels_create(user_A["token"], "public_channel", True)
    channel_join(user_B["token"], public_channel["channel_id"])

    with pytest.raises(InputError):
        channel_removeowner(
            user_A["token"], public_channel["channel_id"], user_B["u_id"]
        )


def test_remove_owner_by_non_owner():
    clear_database()
    user_A, user_B = register_n_users(2)
    public_channel = channels_create(user_A["token"], "public_channel", True)
    channel_join(user_B["token"], public_channel["channel_id"])

    with pytest.raises(AccessError):
        channel_removeowner(
            user_B["token"], public_channel["channel_id"], user_A["u_id"]
        )


def test_channel_removeowner_multiple_channels():
    clear_database()
    usera, userb = register_n_users(2)
    channela = channels_create(usera["token"], "a", is_public=True)["channel_id"]
    channelb = channels_create(userb["token"], "b", is_public=True)["channel_id"]

    channel_join(usera["token"], channelb)
    channel_addowner(userb["token"], channelb, usera["u_id"])
    channel_removeowner(userb["token"], channelb, userb["u_id"])
    channel_removeowner(usera["token"], channelb, usera["u_id"])

    channel_removeowner(usera["token"], channela, usera["u_id"])


# There are two situations when we remove the owner and there is only one owner:
# 1: The channel has other member so we pick a random user to be the owner
# 2: The channel only contain the owner itself so the channel should be removed
# The two tests below will test these two situation repectively
def test_remove_the_only_owner():
    clear_database()
    user_A, user_B = register_n_users(2)
    public_channel = channels_create(user_A["token"], "public_channel", True)
    channel_join(user_B["token"], public_channel["channel_id"])
    channel_removeowner(user_A["token"], public_channel["channel_id"], user_A["u_id"])
    details = channel_details(user_B["token"], public_channel["channel_id"])
    expected_owner_ids = [user_B["u_id"]]
    assert_contains_users_id(details["owner_members"], expected_owner_ids)


def test_remove_owner_with_the_only_member():
    clear_database()
    user_A = register_n_users(1)
    public_channel = channels_create(user_A["token"], "public_channel", True)
    channel_removeowner(user_A["token"], public_channel["channel_id"], user_A["u_id"])
    with pytest.raises(InputError):
        channel_details(user_A["token"], public_channel["channel_id"])


def test_channel_invite_from_unauthorised_user():
    clear_database()
    usera, userb = register_n_users(2)
    channel_id = channels_create(userb["token"], "userb_channel", False)["channel_id"]

    with pytest.raises(AccessError):
        assert channel_invite(usera["token"], channel_id, userb["u_id"])


def test_channel_invite_invalid_id():
    clear_database()
    user = register_n_users(1)
    channel_id = channels_create(user["token"], "ch", is_public=False)["channel_id"]

    with pytest.raises(InputError):
        channel_invite(user["token"], channel_id, u_id=-1)


def test_channel_invite_invalid_token():
    clear_database()
    with pytest.raises(AccessError):
        channel_invite(-1, 0, 0)


def test_channel_invite_simple():
    clear_database()
    usera, userb = register_n_users(2)
    channel_id = channels_create(userb["token"], "userb_channel", False)["channel_id"]

    usera_info = {
        "u_id": usera["u_id"],
        "name_first": auth_get_user_data_from_id(usera["u_id"])["first_name"],
        "name_last": auth_get_user_data_from_id(usera["u_id"])["last_name"],
    }

    channel_members_info = channel_details(userb["token"], channel_id)["all_members"]
    assert usera_info not in channel_members_info

    channel_invite(userb["token"], channel_id, usera["u_id"])
    updated_channel_members_info = channel_details(userb["token"], channel_id)[
        "all_members"
    ]
    assert usera_info in updated_channel_members_info


def test_channel_invite_member_already_in_channel():
    clear_database()
    usera, userb = register_n_users(2)
    channel_id = channels_create(userb["token"], "userb_channel", True)["channel_id"]

    usera_info = {
        "u_id": usera["u_id"],
        "name_first": auth_get_user_data_from_id(usera["u_id"])["first_name"],
        "name_last": auth_get_user_data_from_id(usera["u_id"])["last_name"],
    }

    channel_join(usera["token"], channel_id)
    channel_invite(userb["token"], channel_id, usera["u_id"])
    channel_members_info = channel_details(userb["token"], channel_id)["all_members"]

    usera_count = 0
    for user in channel_members_info:
        if user == usera_info:
            usera_count = usera_count + 1
    assert usera_count == 1


def test_channel_invite_multiple_channels():
    clear_database()
    usera, userb = register_n_users(2)
    channela = channels_create(usera["token"], "usera_ch", is_public=False)
    channelb = channels_create(userb["token"], "userb_ch", is_public=False)

    channel_invite(usera["token"], channela["channel_id"], userb["u_id"])

    detailsa = channel_details(usera["token"], channela["channel_id"])
    detailsb = channel_details(userb["token"], channelb["channel_id"])

    assert_contains_users_id(detailsa["all_members"], [usera["u_id"], userb["u_id"]])
    assert_contains_users_id(detailsa["owner_members"], [usera["u_id"]])

    assert_contains_users_id(detailsb["all_members"], [userb["u_id"]])
    assert_contains_users_id(detailsb["owner_members"], [userb["u_id"]])


def test_channel_invite_invalid_channel_id():
    clear_database()
    usera, userb = register_n_users(2)

    with pytest.raises(InputError):
        channel_invite(usera["token"], channel_id=-1, u_id=userb["u_id"])


# Helper function

# Check whether the user is the owner or member of a channel
def assert_contains_users_id(user_details, expected_user_ids):
    """
    Checks whether the expected users' id are in the users details list.

    >>> user_details = channel_details(token, channel_id)['all_members']
    >>> expected_members_id = [usera['u_id'], userb['u_id']]
    >>> assert_contains_users_id(user_details, expected_members_id)
    """

    assert len(user_details) == len(
        expected_user_ids
    ), f"expect {len(expected_user_ids)} users, but got {len(user_details)}"

    for user in user_details:
        assert (
            user["u_id"] in expected_user_ids
        ), f"channel contains unexpected user {user['u_id']}"
        expected_user_ids.remove(user["u_id"])
    assert (
        len(expected_user_ids) == 0
    ), f"users ${expected_user_ids} where not found in the channel"