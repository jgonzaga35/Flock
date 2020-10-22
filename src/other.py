from database import database, clear_database
from auth import auth_get_current_user_id_from_token
from user import get_user_details


def clear():
    clear_database()


def users_all(token):
    users = []

    # authenticate user
    auth_get_current_user_id_from_token(token)

    for user in database["users"].values():
        user_info = get_user_details(user)["user"]
        users.append(user_info)

    return {"users": users} 


def admin_userpermission_change(token, u_id, permission_id):
    pass


def search(token, query_str):
    return {
        "messages": [
            {
                "message_id": 1,
                "u_id": 1,
                "message": "Hello world",
                "time_created": 1582426789,
            }
        ],
    }
