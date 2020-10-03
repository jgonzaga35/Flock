import pytest
from auth import auth_login, auth_logout, auth_register
from database import clear_database
from error import InputError

def register_new_account():
    return auth_register('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')

# Successful cases for auth_login
def test_login_success_case():
    clear_database()
    register_new_account()
    auth_login('validemail@gmail.com', '123abc!@#')

# Fail cases for auth_login
def test_login_fail_case():
    clear_database()
    register_new_account()
    with pytest.raises(InputError):
        auth_login('didntusethis@gmail.com', '123abcd!@#')  # Never registered
    with pytest.raises(InputError):
        auth_login('validemail@gmail.com', '123')           # Wrong password

def test_login_invalid_email():
    clear_database()
    with pytest.raises(InputError):
        auth_login('didntusethis@gmail', '123abcd!@#')
    with pytest.raises(InputError):
        auth_login('didntusethis.com', '123abcd!@#')

# Tests for auth_logout
def test_logout_fail_logout_twice():
    clear_database()
    result = register_new_account()
    token = result['token']
    auth_logout(token)
    assert auth_logout(token)['is_success'] == False

def test_logout_fail_non_exist_user():
    clear_database()
    token = "non exist"
    assert auth_logout(token)['is_success'] == False

def test_logout_success():
    clear_database()
    result = register_new_account()
    token = result['token']
    assert auth_logout(token)['is_success'] == True

# Successful cases for auth_register
def test_register_success_case():
    clear_database()
    register_new_account()

# Fail cases for auth_register
def test_auth_register_invalid_email():
    clear_database()
    with pytest.raises(InputError):
        auth_register('didntusethis@gmail', '123abcd!@#', 'Peter', 'Li')
    with pytest.raises(InputError):
        auth_register('didntusethis.com', '123abcd!@#', 'Peter', 'Li')

def test_auth_register_used_email():
    clear_database()
    register_new_account()
    with pytest.raises(InputError):
        auth_register('validemail@gmail.com', '123abcd!@#', 'Peter', 'Li')

def test_auth_register_weak_password():
    clear_database()
    with pytest.raises(InputError):
        auth_register('validemail@gmail.com', 'LOL', 'Peter', 'Li')

def test_auth_register_wrong_name():
    clear_database()
    with pytest.raises(InputError):
        auth_register('validemail@gmail.com', '123abc!@#', 'dsjfsdkfjsdafklsdjfsdklfjlkasdkflasdjkfjklsdafjklasdkjlflksjadfjklsdakjfjkdsaflkjadslkflkasdklfklkljdsafl', 'Everest')
    with pytest.raises(InputError):
        auth_register('validemail@gmail.com', '123abc!@#', 'Hayden', 'asdfjskaldjflsadfjklasdfjaksldfjakjsdhfsjkadhfkjasdhfkjsdhfkjasdfhkjsadhfkjasdhf')
