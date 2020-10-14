import time
from database import database
from auth import auth_get_current_user_id_from_token
from channel import get_channel_from_id
from error import AccessError, InputError


def message_send(token, channel_id, message):
    user_id = auth_get_current_user_id_from_token(token)
    channel = get_channel_from_id(channel_id)

    if user_id not in channel["all_members_id"]:
        raise AccessError(
            f"user {user_id} needs to be a member of this channel to send a message"
        )

    if len(message) > 1000:
        raise InputError(
            f"No one is going to read a {len(message)} character long message!"
        )

    message_id = database["messages_id_head"]

    channel["messages"][message_id] = {
        "message_id": message_id,
        "u_id": user_id,
        "message": message,
        "time_created": time.time(),
    }

    database["messages_id_head"] += 1

    return {"message_id": message_id}


def message_remove(token, message_id):
    return {}


def message_edit(token, message_id, message):
    return {}
