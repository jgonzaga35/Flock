from auth import auth_login, auth_logout, auth_register
from error import InputError, AccessError
import pytest

@pytest.fixture
def login_account():
    return auth_register('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')

def test_login_fail_case():
    result = login_account
    with pytest.raises(InputError) as e:
        auth_login('didntusethis@gmail.com', '123abcd!@#')  # Never registered
        auth_login('validemail@gmail.com', '123')           # Wrong password

def test_login_invalid_email():
    with pytest.raises(InputError) as e:
        auth_login('didntusethis@gmail', '123abcd!@#')
        auth_login('didntusethis.com', '123abcd!@#')

def test_login_success_case():
    result = login_account
    auth_login('validemail@gmail.com', '123abc!@#')

# Successful cases for aut_register


# Fail cases for auth_register
def auth_register_invalid_email():
    with pytest.raises(InputError) as e:
        auth_register('didntusethis@gmail', '123abcd!@#')
        auth_register('didntusethis.com', '123abcd!@#')

def auth_register_used_email():
    result = login_account
    with pytest.raises(InputError) as e:
        auth_register('validemail@gmail.com', '123abcd!@#', 'Peter', 'Li')

def auth_register_weak_password():
    with pytest.raises(InputError) as e:
        auth_register('validemail@gmail.com', 'LOL', 'Peter', 'Li')

def auth_register_wrong_name():
    with pytest.raises(InputError) as e:
        auth_register('validemail@gmail.com', '123abc!@#', 'dsjfsdkfjsdafklsdjfsdklfjlkasdkflasdjkfjklsdafjklasdkjlflksjadfjklsdakjfjkdsaflkjadslkflkasdklfklkljdsafl', 'Everest')
        auth_register('validemail@gmail.com', '123abc!@#', 'Hayden', 'asdfjskaldjflsadfjklasdfjaksldfjakjsdhfsjkadhfkjasdhfkjsdhfkjasdfhkjsadhfkjasdhf')
