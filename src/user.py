from database import database
from error import InputError, AccessError


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
    return {}


def user_profile_setemail(token, email):
    return {}


def user_profile_sethandle(token, handle_str):
    return {}
