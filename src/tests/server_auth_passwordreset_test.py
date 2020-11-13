import requests
from test_helpers import (
    url,
    http_register_n_users,
    get_reset_code_from_user_id,
    contains_reset_code,
)

VALID_LOGIN_INFO = {"email": "validemail@gmail.com", "password": "123abc!@#"}
EMAIL = "validemail@gmail.com"


def register_new_account(url):
    return requests.post(
        url + "/auth/register",
        json={
            "email": "validemail@gmail.com",
            "password": "123abc!@#",
            "name_first": "Hayden",
            "name_last": "Everest",
        },
    ).json()


## PASSWORDRESET REQUEST TESTS ####

# Testing that http wrapper successfully calls passwordreset request function
# for valid input and returns
def test_server_passwordreset_request_success(url):
    requests.delete(url + "clear")
    register_new_account(url)

    # Ensure that passwordreset/request is called
    # Ensure that passwordreset/request returns correct return value
    response = requests.post(url + "auth/passwordreset/request", json={"email": EMAIL})
    assert response.status_code == 200
    assert response.json() == {}


# passwordreset/request fails due to invalid email
def test_server_passwordreset_request_invalid_email(url):
    requests.delete(url + "clear")
    register_new_account(url)
    invalid_email = "12345"

    response = requests.post(
        url + "auth/passwordreset/request",
        json={"email": invalid_email},
    )
    assert response.status_code == 400


## PASSWORDRESET RESET TESTS ####

# Test that password reset fails for invalid password
def test_server_passwordreset_reset_invalid_password(url):
    requests.delete(url + "clear")
    register_new_account(url)

    # Request to reset password
    response = requests.post(
        url + "auth/passwordreset/request",
        json={"email": EMAIL},
    )
    assert response.status_code == 200

    invalid_password = "a"
    response = requests.post(
        url + "auth/passwordreset/reset",
        json={"reset_code": "1234567890", "new_password": invalid_password},
    )
    assert response.status_code == 400


# Test that password reset fails for invalid reset code
def test_server_passwordreset_reset_invalid_reset_code(url):
    requests.delete(url + "clear")
    register_new_account(url)

    # Request to reset password
    response = requests.post(
        url + "auth/passwordreset/request",
        json={"email": EMAIL},
    )
    assert response.status_code == 200

    # Try to reset password with an invalid reset code but valid password
    invalid_reset_code = "invalidresetcode"
    valid_password = "ValidPassword123"
    response = requests.post(
        url + "auth/passwordreset/reset",
        json={"reset_code": invalid_reset_code, "new_password": valid_password},
    )
    assert response.status_code == 400
