import requests
from test_helpers import (
    url,
    http_register_n_users,
    get_reset_code_from_user_id,
)
from auth import auth_get_user_data_from_id
from auth_passwordreset import generate_reset_code
from test_helpers import get_reset_code_from_user_id

# passwordreset/request fails due to invalid email
def test_passwordreset_request_invalid_email(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    invalid_email = "12345"

    response = requests.post(
        url + "auth/passwordreset/request",
        json={"email": invalid_email},
    ).json()

    assert response.status_code == 400


# Test that database successfully stores reset code
def test_passwordreset_request_success():
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    response = requests.post(
        url + "auth/passwordreset/request",
        json={"email": user["email"]},
    ).json()
    assert response.status_code == 200


# Test that password reset fails for invalid password
def test_passwordreset_reset_invalid_password():
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    user = auth_get_user_data_from_id(user["u_id"])

    response = requests.post(
        url + "auth/passwordreset/request",
        json={"email": user["email"]},
    ).json()
    assert response.status_code == 200

    valid_reset_code = get_reset_code_from_user_id(user["u_id"])
    invalid_password = "a"

    response = requests.post(
        url + "auth/passwordreset/reset",
        json={"reset_code": valid_reset_code, "new_password": invalid_password},
    ).json()
    assert response.status_code == 400


# Test that password reset fails for invalid reset code
def test_passwordreset_reset_invalid_reset_code():
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    user = auth_get_user_data_from_id(user["u_id"])

    response = requests.post(
        url + "auth/passwordreset/request",
        json={"email": user["email"]},
    ).json()
    assert response.status_code == 200

    invalid_reset_code = "invalidresetcode"
    valid_password = "ValidPassword123"

    response = requests.post(
        url + "auth/passwordreset/reset",
        json={"reset_code": invalid_reset_code, "new_password": valid_password},
    ).json()
    assert response.status_code == 400


# Test that passwordreset successfully sresets password
def test_passwordreset_reset_success():
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    # Logout
    response = requests.post(
        url + "auth/logout",
        json={"token": user["token"]},
    ).json()
    assert response.status_code == 200

    # Request to reset password
    user_data = auth_get_user_data_from_id(user["u_id"])
    u_id = user_data["id"]
    email = user_data["email"]
    response = requests.post(
        url + "auth/passwordreset/request",
        json={"email": email},
    ).json()

    # Get reset code and use to reset password
    reset_code = get_reset_code_from_user_id(u_id)
    new_password = "NewPassword123"
    assert len(reset_code) == 10
    response = requests.post(
        url + "auth/passwordreset/reset",
        json={"reset_code": reset_code, "new_password": new_password},
    ).json()
    assert response.status_code == 200

    # Assert user can login with old password
    response = requests.post(
        url + "auth/login",
        json={"email": email, "password": new_password},
    ).json()
    assert response.status_code == 200

    # Ensure user cannot login with old password
    response = requests.post(
        url + "auth/logout",
        json={"token": response["token"]},
    ).json()
    assert response.status_code == 400


def test_passwordreset_reset_double_reset():
    requests.delete(url + "clear")
    user = http_register_n_users(1)

    # Logout
    response = requests.post(
        url + "auth/logout",
        json={"token": user["token"]},
    ).json()
    assert response.status_code == 200

    user_data = auth_get_user_data_from_id(user["u_id"])
    u_id = user_data["id"]
    email = user_data["email"]
    old_password = "passwordthatislongenough0"

    # Request to reset password
    response = requests.post(
        url + "auth/resetpassword/request",
        json={"email": email},
    ).json()
    assert response.status_code == 200

    # Reset password
    reset_code = get_reset_code_from_user_id(u_id)
    new_password = "NewPassword123"
    response = requests.post(
        url + "auth/resetpassword/reset",
        json={"reset_code": reset_code, "new_password": new_password},
    ).json()
    assert response.status_code == 200

    # Assert user can login with new password
    response = requests.post(
        url + "auth/login",
        json={"email": email, "password": new_password},
    ).json()
    assert response.status_code == 200

    # Ensure user cannot login with old password
    response = requests.post(
        url + "auth/logout",
        json={"token": response["token"]},
    ).json()
    assert response.status_code == 200

    response = requests.post(
        url + "auth/resetpassword/reset",
        json={"reset_code": reset_code, "new_password": "NewPassWord2"},
    )
    assert response.status_code == 400


def test_passwordreset_reset_success_twice():
    requests.delete(url + "clear")
    user = http_register_n_users(1)

    # Logout
    response = requests.post(
        url + "auth/logout",
        json={"token": user["token"]},
    ).json()
    assert response.status_code == 200

    user_data = auth_get_user_data_from_id(user["u_id"])
    u_id = user_data["id"]
    email = user_data["email"]
    old_password = "passwordthatislongenough0"

    # Request to reset password
    response = requests.post(
        url + "auth/resetpassword/request",
        json={"email": email},
    ).json()
    assert response.status_code == 200

    # Reset password
    reset_code = get_reset_code_from_user_id(u_id)
    new_password = "NewPassword123"
    response = requests.post(
        url + "auth/resetpassword/reset",
        json={"reset_code": reset_code, "new_password": new_password},
    ).json()
    assert response.status_code == 200

    # Assert user can login with new password
    response = requests.post(
        url + "auth/login",
        json={"email": email, "password": new_password},
    ).json()
    assert response.status_code == 200

    # Request to reset password
    response = requests.post(
        url + "auth/resetpassword/request",
        json={"email": email},
    ).json()
    assert response.status_code == 200

    # Reset password
    reset_code_2 = get_reset_code_from_user_id(u_id)
    assert reset_code != reset_code_2
    new_password_2 = "NewPassword124"
    response = requests.post(
        url + "auth/resetpassword/reset",
        json={"reset_code": reset_code_2, "new_password": new_password_2},
    ).json()
    assert response.status_code == 200

    # Assert user can login with new password
    response = requests.post(
        url + "auth/login",
        json={"email": email, "password": new_password_2},
    ).json()
    assert response.status_code == 200
