from auth import auth_login, auth_logout, auth_register
import pytest

@pytest.fixture
def login_account():
    return auth_register('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')

def test_login_FailCase():
    result = login_account
    with pytest.raises(InputError) as e:
        auth_login('didntusethis@gmail.com', '123abcd!@#')  # Never registered
        auth_login('validemail@gmail.com', '123')           # Wrong password

def test_login_InvalidEmail():
    with pytest.raises(InputError) as e:
        auth_login('didntusethis@gmail', '123abcd!@#')
        auth_login('didntusethis.com', '123abcd!@#')

def test_login_SuccessCase():
    result = login_account
    auth.auth_login('validemail@gmail.com', '123abc!@#')

def auth_logout_test():
    pass

def auth_register():
    pass
