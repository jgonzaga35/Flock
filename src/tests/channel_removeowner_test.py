import pytest
from channels import channels_create
from channel import channel_addowner, channel_details, channel_removeowner, channel_join
from other import clear
from test_helpers import assert_contains_users_id, register_n_users
from error import AccessError


def test_channel_removeowner_admin_remaining_owners():
    clear()
    admin, usera, userb = register_n_users(3, include_admin=True)

    # A creates channel and adds B as an owner
    channel_id = channels_create(usera["token"], "", is_public=True)["channel_id"]
    channel_addowner(usera["token"], channel_id, userb["u_id"])

    # admin removes user A
    channel_removeowner(admin["token"], channel_id, usera["u_id"])

    # there should only be user B left
    details = channel_details(usera["token"], channel_id)
    assert_contains_users_id(details["owner_members"], [userb["u_id"]])
    assert_contains_users_id(details["all_members"], [userb["u_id"], usera["u_id"]])


def test_channel_removeowner_admin_last_owner_with_no_members():
    clear()
    admin, usera = register_n_users(2, include_admin=True)

    # user a creates a channel
    channel_id = channels_create(usera["token"], "", is_public=True)["channel_id"]
    # admin removes him from his channel
    channel_removeowner(admin["token"], channel_id, usera["u_id"])

    with pytest.raises(AccessError):
        # usera can't access the channel anymore, because he is not a member
        # (there are no members in the channel anymore)
        channel_details(usera["token"], channel_id)


def test_channel_removeowner_admin_last_owner_with_members():
    clear()
    admin, usera, userb = register_n_users(3, include_admin=True)
    # A creates his channel and B joins
    channel_id = channels_create(usera["token"], "", is_public=True)["channel_id"]
    channel_join(userb["token"], channel_id)

    # admin removes A as an owner
    channel_removeowner(admin["token"], channel_id, usera["u_id"])

    # B becomes an owner, and A is just a regular member
    details = channel_details(usera["token"], channel_id)
    assert_contains_users_id(details["owner_members"], [userb["u_id"]])
    assert_contains_users_id(details["all_members"], [userb["u_id"], usera["u_id"]])
