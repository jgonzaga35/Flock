from channel import channel_removeowner, channel_join, channel_addowner, channel_details
from channels import channels_create
from other import clear
from test_helpers import register_n_users, assert_contains_users_id
import pytest
from error import AccessError, InputError


def test_remove_owner_invalid_token():
    clear()
    with pytest.raises(AccessError):
        channel_removeowner(-1, 0, 0)


def test_remove_user_successfully():
    clear()
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
    clear()
    user_A, user_B = register_n_users(2)
    public_channel = channels_create(user_A["token"], "public_channel", True)
    channel_join(user_B["token"], public_channel["channel_id"])
    channel_addowner(user_A["token"], public_channel["channel_id"], user_B["u_id"])

    with pytest.raises(InputError):
        invalid_channel_id = 233
        channel_removeowner(user_A["token"], invalid_channel_id, user_B["u_id"])


def test_remove_owner_to_non_owner():
    clear()
    user_A, user_B = register_n_users(2)
    public_channel = channels_create(user_A["token"], "public_channel", True)
    channel_join(user_B["token"], public_channel["channel_id"])

    with pytest.raises(InputError):
        channel_removeowner(
            user_A["token"], public_channel["channel_id"], user_B["u_id"]
        )


def test_remove_owner_by_non_owner():
    clear()
    user_A, user_B = register_n_users(2)
    public_channel = channels_create(user_A["token"], "public_channel", True)
    channel_join(user_B["token"], public_channel["channel_id"])

    with pytest.raises(AccessError):
        channel_removeowner(
            user_B["token"], public_channel["channel_id"], user_A["u_id"]
        )


def test_channel_removeowner_multiple_channels():
    clear()
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
# 2: The channel only contain the owner himself and we let the owner leave that channel
# The two tests below will test these two situation repectively
def test_remove_the_only_owner():
    clear()
    user_A, user_B = register_n_users(2)
    public_channel = channels_create(user_A["token"], "public_channel", True)
    channel_join(user_B["token"], public_channel["channel_id"])
    channel_removeowner(user_A["token"], public_channel["channel_id"], user_A["u_id"])
    details = channel_details(user_B["token"], public_channel["channel_id"])
    expected_owner_ids = [user_B["u_id"]]
    assert_contains_users_id(details["owner_members"], expected_owner_ids)


def test_remove_owner_with_the_only_member():
    clear()
    # register a owner and remove its owner
    user_A = register_n_users(1)
    public_channel = channels_create(user_A["token"], "public_channel", True)
    channel_removeowner(user_A["token"], public_channel["channel_id"], user_A["u_id"])

    # if a owner is the only member of a channel, we expect him leaving the channel after
    # remove owner, so he won't have authority to access the channel
    with pytest.raises(AccessError):
        channel_details(user_A["token"], public_channel["channel_id"])
