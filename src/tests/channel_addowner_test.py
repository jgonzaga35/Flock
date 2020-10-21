import pytest
from channels import channels_create
from channel import channel_addowner, channel_details
from database import clear_database
from test_helpers import assert_contains_users_id, register_n_users


def test_channel_addowner_admin_public_channel():
    clear_database()
    admin, usera = register_n_users(2, include_admin=True)
    channel_id = channels_create(usera["token"], "channel", is_public=True)[
        "channel_id"
    ]
    channel_addowner(admin["token"], channel_id, admin["u_id"])
    details = channel_details(usera["token"], channel_id)
    assert_contains_users_id(details["all_members"], [admin["u_id"], usera["u_id"]])
    assert_contains_users_id(details["owner_members"], [admin["u_id"], usera["u_id"]])


def test_channel_addowner_admin_private_channel():
    clear_database()
    admin, usera = register_n_users(2, include_admin=True)
    channel_id = channels_create(usera["token"], "channel", is_public=False)[
        "channel_id"
    ]
    channel_addowner(admin["token"], channel_id, admin["u_id"])
    details = channel_details(usera["token"], channel_id)
    assert_contains_users_id(details["all_members"], [admin["u_id"], usera["u_id"]])
    assert_contains_users_id(details["owner_members"], [admin["u_id"], usera["u_id"]])
