import pytest
from test_helpers import register_n_users, assert_contains_users_id
from channel import channel_join, channel_details, channel_leave
from channels import channels_create
from other import clear
from error import InputError, AccessError


def test_channel_join_admin_on_private_channel():
    clear()
    admin, usera = register_n_users(2, include_admin=True)

    channel_id = channels_create(usera["token"], "channel", is_public=False)[
        "channel_id"
    ]

    channel_join(admin["token"], channel_id)

    details = channel_details(usera["token"], channel_id)
    assert_contains_users_id(details["all_members"], [admin["u_id"], usera["u_id"]])
    assert_contains_users_id(details["owner_members"], [usera["u_id"]])


def test_join_invalid_token():
    clear()
    with pytest.raises(AccessError):
        channel_join(-1, 0)


def test_channel_join_multiple_channels():
    clear()
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
    clear()
    user_A, user_B = register_n_users(2)
    public_channel = channels_create(user_A["token"], "Channel_A", True)
    channel_join(user_B["token"], public_channel["channel_id"])
    details = channel_details(user_A["token"], public_channel["channel_id"])
    expected_member_ids = [user_A["u_id"], user_B["u_id"]]

    assert_contains_users_id(details["all_members"], expected_member_ids)


# user try to join a channel with invalid channel id
def test_join_channel_with_invalid_channel_id():
    clear()
    user = register_n_users(1)
    invalid_channel_id = 233

    with pytest.raises(InputError):
        channel_join(user["token"], invalid_channel_id)


# join a user without authority to a channel
def test_join_channel_without_authority():
    clear()
    user_A, user_B = register_n_users(2)
    channel = channels_create(
        user_A["token"], "Private_channel", False
    )  # Create a new private channel

    with pytest.raises(AccessError):
        channel_join(user_B["token"], channel["channel_id"])


def test_join_empty_channel():
    """
    If a user join a channel with no member, he should automatically becomes the owner
    """
    clear()

    # user_a create a channel and leave from there, user_b join the
    # channel with no member.
    user_a, user_b = register_n_users(2)
    channel = channels_create(
        user_a["token"], "public_channel", True
    )  # Create a public channel
    channel_leave(user_a["token"], channel["channel_id"])
    channel_join(user_b["token"], channel["channel_id"])

    # Verify that user_b automatically be the owner of that channel
    details = channel_details(user_b["token"], channel["channel_id"])
    expect_owner_in_channel = [user_b["u_id"]]
    assert_contains_users_id(details["owner_members"], expect_owner_in_channel)
