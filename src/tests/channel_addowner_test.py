from channel import channel_addowner, channel_join, channel_details
from channels import channels_create
from other import clear
from test_helpers import register_n_users, assert_contains_users_id
import pytest
from error import AccessError, InputError


def test_add_owner_invalid_id():
    clear()
    usera, userb = register_n_users(2)
    channel_id = channels_create(usera["token"], "channel_name", is_public=True)[
        "channel_id"
    ]
    channel_join(userb["token"], channel_id)

    with pytest.raises(AccessError):
        channel_addowner(-1, channel_id, userb["u_id"])


# We assume when a user outside a channel being added as owner of this channel,
# he automatically become an member of this channel
def test_add_non_members_as_owner():
    clear()
    user_a, user_b = register_n_users(2)
    public_channel = channels_create(user_a["token"], "public_channel", True)

    # invite user from outside this channel
    channel_addowner(user_a["token"], public_channel["channel_id"], user_b["u_id"])
    details = channel_details(user_a["token"], public_channel["channel_id"])
    expect_owner_in_channel = [user_a["u_id"], user_b["u_id"]]
    expect_member_in_channel = [user_a["u_id"], user_b["u_id"]]

    # We assume user who is invited will be the member and owner of this channel
    assert_contains_users_id(details["owner_members"], expect_owner_in_channel)
    assert_contains_users_id(details["all_members"], expect_member_in_channel)


def test_add_owner_successfully():
    clear()
    user_A, user_B = register_n_users(2)
    public_channel = channels_create(user_A["token"], "public_channel", True)
    channel_join(user_B["token"], public_channel["channel_id"])

    # user_A add user_B as onwer, gotta check whether user_B is in owner list
    channel_addowner(user_A["token"], public_channel["channel_id"], user_B["u_id"])
    details = channel_details(user_A["token"], public_channel["channel_id"])
    expect_owner_in_channel = [user_A["u_id"], user_B["u_id"]]
    assert_contains_users_id(details["owner_members"], expect_owner_in_channel)


def test_add_owner_with_invalid_channel_id():
    clear()
    user_A, user_B = register_n_users(2)
    public_channel = channels_create(user_A["token"], "public_channel", True)
    channel_join(user_B["token"], public_channel["channel_id"])
    with pytest.raises(InputError):
        invalid_channel_id = 233
        channel_addowner(user_A["token"], invalid_channel_id, user_B["u_id"])


def test_add_owner_repeatedly():
    clear()
    user_A, user_B = register_n_users(2)
    public_channel = channels_create(user_A["token"], "public_channel", True)
    channel_join(user_B["token"], public_channel["channel_id"])
    channel_addowner(user_A["token"], public_channel["channel_id"], user_B["u_id"])
    with pytest.raises(InputError):
        channel_addowner(user_A["token"], public_channel["channel_id"], user_B["u_id"])


def test_add_invalid_user_to_owner():
    clear()
    user_A = register_n_users(1)
    private_channel = channels_create(user_A["token"], "private_channel", False)
    invalid_uid = 233
    with pytest.raises(InputError):
        channel_addowner(user_A["token"], private_channel["channel_id"], invalid_uid)


# We assume all of the user are in a public channel
# One of them are the owner whereas other two are common user in this channel
def test_add_owner_by_non_owner():
    clear()
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


def test_channel_addowner_admin_public_channel():
    clear()
    admin, usera = register_n_users(2, include_admin=True)
    channel_id = channels_create(usera["token"], "channel", is_public=True)[
        "channel_id"
    ]
    channel_addowner(admin["token"], channel_id, admin["u_id"])
    details = channel_details(usera["token"], channel_id)
    assert_contains_users_id(details["all_members"], [admin["u_id"], usera["u_id"]])
    assert_contains_users_id(details["owner_members"], [admin["u_id"], usera["u_id"]])


def test_channel_addowner_admin_private_channel():
    clear()
    admin, usera = register_n_users(2, include_admin=True)
    channel_id = channels_create(usera["token"], "channel", is_public=False)[
        "channel_id"
    ]
    channel_addowner(admin["token"], channel_id, admin["u_id"])
    details = channel_details(usera["token"], channel_id)
    assert_contains_users_id(details["all_members"], [admin["u_id"], usera["u_id"]])
    assert_contains_users_id(details["owner_members"], [admin["u_id"], usera["u_id"]])
