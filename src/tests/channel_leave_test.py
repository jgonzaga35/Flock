from channel import channel_leave, channel_details, channel_join
from channels import channels_create
from test_helpers import register_n_users, assert_contains_users_id
import pytest
from error import InputError, AccessError
from other import clear


def test_leave_invalid_token():
    clear()
    with pytest.raises(AccessError):
        channel_leave(-1, 0)


# user successfully leave the channel
def test_leave_channel_successfully():
    clear()
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


# If a user tries to leave a private channel that they are not part of
def test_inexist_user_leave_channel_private():
    clear()
    user_A, user_B = register_n_users(2)
    private_channel = channels_create(
        user_A["token"], "private_channel", False
    )  # a private channel

    with pytest.raises(AccessError):
        channel_leave(user_B["token"], private_channel["channel_id"])


# If a user tries to leave a public channel that they are not part of
def test_inexist_user_leave_channel_public():
    clear()
    user_A, user_B = register_n_users(2)
    public_channel = channels_create(
        user_A["token"], "public_channel", True
    )  # User A create a public channel and

    with pytest.raises(AccessError):
        channel_leave(user_B["token"], public_channel["channel_id"])


def test_leave_channel_id_invalid():
    clear()
    user = register_n_users(1)
    channel_id = channels_create(user["token"], "channel_A", True)["channel_id"]
    invalid_channel_id = channel_id + 1

    with pytest.raises(InputError):
        channel_leave(user["token"], invalid_channel_id)
