import pytest
from auth import (
    auth_login,
    auth_logout,
    auth_register,
    auth_get_user_data_from_id,
)
from auth_passwordreset import (
    auth_passwordreset_reset,
    auth_passwordreset_request,
)
from test_helpers import (
    register_n_users,
    contains_reset_code,
    get_reset_code_from_user_id,
)
from other import clear
from error import InputError, AccessError
from hashlib import sha256

# Testing that passwordreset_request does not work for invalid emails.
def test_passwordreset_request_invalid_email():
    clear()
    register_n_users(1)
    invalid_email = "12345"

    with pytest.raises(InputError):
        auth_passwordreset_request(invalid_email)


# Test that the database has successfully stored the reset code for a user.
def test_passwordreset_request_success():
    clear()
    user = register_n_users(1)
    user = auth_get_user_data_from_id(user["u_id"])
    auth_passwordreset_request(user["email"])

    assert contains_reset_code(user) == True


# Testing that password reset fails for invalid password
def test_passwordreset_reset_invalid_password():
    clear()
    user = register_n_users(1)
    u_id = user["u_id"]
    user = auth_get_user_data_from_id(u_id)
    auth_passwordreset_request(user["email"])

    valid_reset_code = get_reset_code_from_user_id(u_id)
    invalid_password = "a"

    with pytest.raises(InputError):
        auth_passwordreset_reset(valid_reset_code, invalid_password)


# Testing that password reset fails for invalid reset code
def test_passwordreset_reset_invalid_reset_code():
    clear()
    user = register_n_users(1)
    u_id = user["u_id"]
    user = auth_get_user_data_from_id(u_id)
    auth_passwordreset_request(user["email"])

    invalid_reset_code = "invalidresetcode"
    valid_password = "ValidPassword123"

    with pytest.raises(InputError):
        auth_passwordreset_reset(invalid_reset_code, valid_password)


# Testing that passwordreset successfully resets password
def test_passwordreset_reset_success():
    clear()
    user = register_n_users(1)

    # Logout, assert that user can login with old password, then logout again
    assert auth_logout(user["token"])["is_success"] == True

    user_data = auth_get_user_data_from_id(user["u_id"])
    u_id = user_data["id"]
    email = user_data["email"]
    old_password = "passwordthatislongenough0"

    token = auth_login(email, old_password)["token"]
    assert auth_logout(token)["is_success"] == True

    # Reset password
    auth_passwordreset_request(email)
    reset_code = get_reset_code_from_user_id(u_id)
    new_password = "NewPassword123"
    auth_passwordreset_reset(reset_code, new_password)

    # Assert user can login with new password
    token = auth_login(email, new_password)["token"]

    # Ensure user cannot login with old password
    auth_logout(token)
    with pytest.raises(InputError):
        assert auth_login(email, old_password)


# Testing that passwordreset reset code only works once
def test_passwordreset_reset_double_reset():
    clear()
    user = register_n_users(1)

    # Logout, assert that user can login with old password, then logout again
    assert auth_logout(user["token"])["is_success"] == True

    user_data = auth_get_user_data_from_id(user["u_id"])
    u_id = user_data["id"]
    email = user_data["email"]
    old_password = "passwordthatislongenough0"

    token = auth_login(email, old_password)["token"]
    assert auth_logout(token)["is_success"] == True

    # Reset password
    auth_passwordreset_request(email)
    reset_code = get_reset_code_from_user_id(u_id)
    new_password = "NewPassword123"
    auth_passwordreset_reset(reset_code, new_password)

    # Assert user can login with new password
    token = auth_login(email, new_password)["token"]

    # Ensure user cannot reset password with old reset code
    auth_logout(token)
    with pytest.raises(InputError):
        assert auth_passwordreset_reset(reset_code, "NewPassWord2")


# Testing for resetting password once, then resetting it successfully again
# This makes sure that the reset codes are always unique.
def test_passwordreset_reset_success_twice():
    clear()
    user = register_n_users(1)

    # Logout, assert that user can login with old password, then logout again
    assert auth_logout(user["token"])["is_success"] == True

    user_data = auth_get_user_data_from_id(user["u_id"])
    u_id = user_data["id"]
    email = user_data["email"]
    old_password = "passwordthatislongenough0"

    token = auth_login(email, old_password)["token"]
    assert auth_logout(token)["is_success"] == True

    # Reset password
    auth_passwordreset_request(email)
    reset_code_1 = get_reset_code_from_user_id(u_id)
    new_password = "NewPassword123"
    auth_passwordreset_reset(reset_code_1, new_password)

    # Assert user can login with new password
    token = auth_login(email, new_password)["token"]
    auth_logout(token)

    # Reset password again and try to login with 2nd new password
    auth_passwordreset_request(email)
    reset_code_2 = get_reset_code_from_user_id(u_id)
    assert reset_code_1 != reset_code_2
    new_password_2 = "NewPassword124"
    auth_passwordreset_reset(reset_code_2, new_password_2)

    token = auth_login(email, new_password_2)["token"]
