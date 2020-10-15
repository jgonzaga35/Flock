from database import database
from error import InputError, AccessError
from auth import auth_get_current_user_id_from_token


def user_profile(token, u_id):

    # Ensure token is valid
    if not token in database["active_tokens"]:
        raise AccessError(f"{token} is not a valid token")

    # Ensure u_id is valid and get the user information from database
    try:
        user = database["users"][u_id]
    except KeyError:
        raise InputError(f"{u_id} is not a valid user id")

    return user


def user_profile_setname(token, name_first, name_last):

    # raises AccessError if token is not active
    u_id = auth_get_current_user_id_from_token(token)
    if isNameTooLong(name_first) or isNameTooLong(name_last):
        raise InputError("Name is too long")

    user = database["users"][u_id]
    user["first_name"] = name_first
    user["last_name"] = name_last


def user_profile_setemail(token, email):
    return {}


def user_profile_sethandle(token, handle_str):
    return {}


# --------------------helper function--------------------
def isNameTooLong(name):
    """
    Take a single last name or first name as input

    If name is too long, return True
    If length of name is good, return False
    """
    if len(name) >= 50:
        return True
    else:
        return False
