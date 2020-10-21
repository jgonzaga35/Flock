import pytest
from test_helpers import register_n_users, assert_contains_users_id
from channel import channel_join, channel_details
from channels import channels_create
from database import clear_database


def test_channel_join_admin_on_private_channel():
    clear_database()
    admin, usera = register_n_users(2, include_admin=True)

    channel_id = channels_create(usera["token"], "channel", is_public=False)[
        "channel_id"
    ]

    channel_join(admin["token"], channel_id)

    details = channel_details(usera["token"], channel_id)
    assert_contains_users_id(details["all_members"], [admin["u_id"], usera["u_id"]])
    assert_contains_users_id(details["owner_members"], [usera["u_id"]])
