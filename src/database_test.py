import pytest
from database import clear_database
from error import InputError
from auth import auth_register, auth_login
from channels import channels_create, channels_listall


def test_database_clear():
    # use some test helpers to populate with some more realistic data

    usera = auth_register("hello@gmail.com", "veryverysafe", "safety", "first")
    userb = auth_register("whaa@gmail.com", "nostress", "safety", "second")

    channels_create(usera['token'], "first_channel", is_public=True)
    channels_create(userb['token'], "second_channel", is_public=True)
    channels_create(userb['token'], "p_channel", is_public=False)

    clear_database()

    # the spec doesn't specifiy which of the InputError and AccessError should
    # be raised first. This is an implementation detail, and since we are doing
    # black box testing, we shouldn't rely on that.
    with pytest.raises(Exception):
        channel_details(usera['token'], "first_channel")

    assert len(channels_listall(usera['token'])) == 0

    with pytest.raises(InputError):
        auth_login("hello@gmail.com", "veryverysafe")

    with pytest.raises(InputError):
        auth_login("whaa@gmail.com", "nostress")