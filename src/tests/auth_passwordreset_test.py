import pytest
from auth import (
    auth_login,
    auth_logout,
    auth_register,
    auth_get_user_data_from_email,
    check_email,
    encrypt,
    jwt_decode,
)
from other import clear
from error import InputError, AccessError
from hashlib import sha256

def is_registered_user(email):
    pass

def register_new_account():
    return auth_register("validemail@gmail.com", "123abc!@#", "Hayden", "Everest")


def test_passwordreset_request_invalid_email():
    clear()
    register_new_account()
    email = "validemail@gmail.com"
    invalid_email = "WhereIsTheLambSauce?"
    
    # Check if the email address is registered in the database
    user = auth_get_user_data_from_email(email)
    
    with pytest.raises(InputError):
        auth_passwordreset_request(invalid_email)

    


