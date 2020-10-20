from database import database, clear_database
from auth import auth_get_current_user_id_from_token
from user import get_user_details
from error import AccessError, InputError


def clear():
    clear_database()


def users_all(token):
    users = []

    # authenticate user
    auth_get_current_user_id_from_token(token)

    for user in database["users"].values():
        user_info = get_user_details(user)
        users.append(user_info)

    return {"users": users}


def admin_userpermission_change(token, u_id, permission_id):
    admin_id = auth_get_current_user_id_from_token(token)

    if database["users"][admin_id]["is_admin"] is False:
        raise AccessError(
            "user isn't a flockr owner, cannot change other user's permission"
        )

    if permission_id != 1 and permission_id != 2:
        raise InputError(f"invalid permission id {permission_id}")

    if u_id not in database["users"]:
        raise InputError(f"invalid user id {u_id}")

    database["users"][u_id]["is_admin"] = permission_id == 1


def search(token, query_str):
    user_id = auth_get_current_user_id_from_token(token)

    matching_messages = []
    # loop through every channel in which the user is a member, add add the
    # matching message to the list
    for channel in database["channels"].values():
        if user_id in channel["all_members_id"]:
            add_matching_messages(channel, query_str, matching_messages)

    return {
        "messages": sorted(
            matching_messages, key=lambda message: message["time_created"], reverse=True
        ),
    }


def add_matching_messages(channel, query_str, matching_messages):
    for message in channel["messages"].values():
        if query_str in message["message"]:
            matching_messages.append(
                {
                    "message_id": message["message_id"],
                    "message": message["message"],
                    "time_created": message["time_created"],
                    "u_id": message["u_id"],
                }
            )
