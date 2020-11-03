from channel import channel_details, formated_user_details_from_user_data
from channels import channels_create
from auth import auth_get_user_data_from_id
from test_helpers import register_n_users
from other import clear
import pytest
from error import InputError, AccessError


def test_channel_details_invalid_token():
    clear()
    with pytest.raises(AccessError):
        channel_details(-1, 0)


def test_channel_details_basic():
    clear()

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
    clear()

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
    clear()
    usera, _ = register_n_users(2)
    with pytest.raises(InputError):
        channel_details(usera["token"], 1)
