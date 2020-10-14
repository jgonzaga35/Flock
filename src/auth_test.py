import pytest
from auth import auth_login, auth_logout, auth_register, auth_get_user_data_from_id
from database import clear_database
from error import InputError


def register_new_account():
    return auth_register("validemail@gmail.com", "123abc!@#", "Hayden", "Everest")


# Successful cases for auth_login
def test_login_success_case():
    clear_database()
    first = register_new_account()
    assert auth_logout(first["token"])["is_success"] == True
    # when we register a new account, the user logged in
    assert auth_login("validemail@gmail.com", "123abc!@#")["u_id"] == first["u_id"]


def test_login_double_login():
    clear_database()
    register_new_account()
    token1 = auth_login("validemail@gmail.com", "123abc!@#")["token"]
    token2 = auth_login("validemail@gmail.com", "123abc!@#")["token"]
    assert token1 == token2
    auth_logout(token1)
    # A user shouldn't be logout twice just because they log in twice
    assert auth_logout(token2)["is_success"] == False


# Fail cases for auth_login
def test_login_fail_case():
    clear_database()
    register_new_account()
    with pytest.raises(InputError):
        auth_login("didntusethis@gmail.com", "123abcd!@#")  # Never registered
    with pytest.raises(InputError):
        auth_login("validemail@gmail.com", "123")  # Wrong password


def test_login_invalid_email():
    clear_database()
    with pytest.raises(InputError):
        auth_login("didntusethis@gmail", "123abcd!@#")
    with pytest.raises(InputError):
        auth_login("didntusethis.com", "123abcd!@#")


# Tests for auth_logout
def test_logout_fail_logout_twice():
    clear_database()
    result = register_new_account()
    token = result["token"]
    auth_logout(token)
    assert auth_logout(token)["is_success"] == False


def test_logout_fail_non_exist_user():
    clear_database()
    token = "non exist"
    assert auth_logout(token)["is_success"] == False


def test_logout_success():
    clear_database()
    result = register_new_account()
    token = result["token"]
    assert auth_logout(token)["is_success"] == True


# Successful cases for auth_register
def test_register_success_case():
    clear_database()
    register_new_account()


# Fail cases for auth_register
def test_auth_register_invalid_email():
    clear_database()
    with pytest.raises(InputError):
        auth_register("didntusethis@gmail", "123abcd!@#", "Peter", "Li")
    with pytest.raises(InputError):
        auth_register("didntusethis.com", "123abcd!@#", "Peter", "Li")


def test_auth_register_used_email():
    clear_database()
    register_new_account()
    with pytest.raises(InputError):
        auth_register("validemail@gmail.com", "123abcd!@#", "Peter", "Li")


def test_auth_register_weak_password():
    clear_database()
    with pytest.raises(InputError):
        auth_register("validemail@gmail.com", "LOL", "Peter", "Li")


def test_auth_register_wrong_name():
    clear_database()
    with pytest.raises(InputError):
        auth_register(
            "validemail@gmail.com",
            "123abc!@#",
            "dsjfsdkfjsdafklsdjfsdklfjlkasdkflasdjkfjklsdafjklasdkjlflksjadfjklsdakjfjkdsaflkjadslkflkasdklfklkljdsafl",
            "Everest",
        )
    with pytest.raises(InputError):
        auth_register(
            "validemail@gmail.com",
            "123abc!@#",
            "Hayden",
            "asdfjskaldjflsadfjklasdfjaksldfjakjsdhfsjkadhfkjasdhfkjsdhfkjasdfhkjsadhfkjasdhf",
        )


def test_auth_helper_user_data_from_invalid_id():
    clear_database()
    with pytest.raises(KeyError):
        auth_get_user_data_from_id(user_id=-1)

def test_handle():
    clear_database()
    id1 = auth_register("validemail1@gmail.com", "123abcd!@#", "Peter", "Li")["u_id"]
    id2 = auth_register("validemail2@gmail.com", "123abcd!@#", "Yoona", "Lim")["u_id"]
    id3 = auth_register("validemail3@gmail.com", "123abcd!@#", "Taeyeon", "KimKimKimKimKimKim")["u_id"]
    id4 = auth_register("validemail4@gmail.com", "123abcd!@#", "Taeyeon", "KimKimKimKimKimKim")["u_id"]

    assert "peterli" == auth_get_user_data_from_id(id1)["handle"]
    assert "yoonalim" == auth_get_user_data_from_id(id2)["handle"]
    assert "taeyeonkimkimkimkimk" == auth_get_user_data_from_id(id3)["handle"]
    assert "taeyeonkimkimkimkimk"[:(20  - len(str(id4)))] + str(id4) == auth_get_user_data_from_id(id4)["handle"]