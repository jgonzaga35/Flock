from auth import auth_get_current_user_id_from_token
from database import database


def get_user_details(user):
    return {
        "u_id": user["id"],
        "email": user["email"],
        "name_first": user["first_name"],
        "name_last": user["last_name"],
        "handle_str": user["handle"] 
    }

def user_profile(token, u_id):
    return {
        "user": {
            "u_id": 1,
            "email": "cs1531@cse.unsw.edu.au",
            "name_first": "Hayden",
            "name_last": "Jacobs",
            "handle_str": "hjacobs",
        },
    }


def user_profile_setname(token, name_first, name_last):
    return {}


def user_profile_setemail(token, email):
    return {}


def user_profile_sethandle(token, handle_str):
    return {}


def users_all(token):
    users = []

    # authenticate user
    auth_get_current_user_id_from_token(token)

    for user in database["users"].values():
        user_info = get_user_details(user) 
        users.append(user_info)

    return users
    