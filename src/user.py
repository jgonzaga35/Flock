from database import database
from error import InputError, AccessError
from auth import (
    auth_get_current_user_id_from_token,
    check_email,
    is_handle_already_used,
)


def user_profile(token, u_id):
    """
    take a valid token and u_id, return a dictionary as below:
    >>> {
        'u_id': user['id'],
        'email': user['email'],
        'name_first': user['first_name'],
        'name_last': user['last_name'],
        'handle_str': user['handle'],
    }
    """
    # Ensure token is valid
    # This function below has error handling built inside
    auth_get_current_user_id_from_token(token)

    # Ensure u_id is valid and get the user information from database
    try:
        user = database["users"][u_id]
    except KeyError:
        raise InputError(f"{u_id} is not a valid user id")

    # We don't directly return user from database since password is included
    return {
        'user': {
            "u_id": user["id"],
            "email": user["email"],
            "name_first": user["first_name"],
            "name_last": user["last_name"],
            "handle_str": user["handle"],
        }
    }


def user_profile_setname(token, name_first, name_last):

    # raises AccessError if token is not active
    u_id = auth_get_current_user_id_from_token(token)

    # If user's first name or last name is more than 50 characters
    if not isNameLengthOK(name_first, 1, 50):
        raise InputError(f"{name_first} is illegal")
    if not isNameLengthOK(name_last, 1, 50):
        raise InputError(f"{name_last} is illegal")

    user = database["users"][u_id]
    user["first_name"] = name_first
    user["last_name"] = name_last


def user_profile_setemail(token, email):

    # raises AccessError if token is not active
    u_id = auth_get_current_user_id_from_token(token)

    # raises InputError if email address is illegal
    check_email(email)

    user = database["users"][u_id]
    user["email"] = email


def user_profile_sethandle(token, handle_str):

    # raises AccessError if token is not active
    u_id = auth_get_current_user_id_from_token(token)

    # raises InputError if there is a duplicated handle
    if is_handle_already_used(handle_str):
        raise InputError(f"{handle_str} has been used")

    # raises InputError if handleis not illegal
    if not isNameLengthOK(handle_str, 3, 20):
        raise InputError(f"length of {handle_str} is illegal")

    user = database["users"][u_id]
    user["handle"] = handle_str


def users_all(token):
    users = []

    # authenticate user
    auth_get_current_user_id_from_token(token)

    for user in database["users"].values():
        user_info = get_user_details(user)
        users.append(user_info)

    return users


# --------------------helper function--------------------
def isNameLengthOK(name, min, max):
    """
    Ensure the length of a name is right
    Input:
    >>> name: target name
    >>> min: minimum length of name
    >>> max: maximum length of name

    If name is not illegal, return True
    If length of name is good, return False
    """
    if len(name) <= max and len(name) >= min:
        return True
    else:
        return False


def get_user_details(user):
    return {
        "u_id": user["id"],
        "email": user["email"],
        "name_first": user["first_name"],
        "name_last": user["last_name"],
        "handle_str": user["handle"],
    }
