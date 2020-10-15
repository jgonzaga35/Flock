from database import database
from auth import auth_get_current_user_id_from_token
from channels import channels_list

from error import AccessError, InputError

from channel import get_channel_from_id
import time

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

    message_id = database["message_id_head"]

    channel["messages"][message_id] = {
        "message_id": message_id,
        "u_id": user_id,
        "message": message,
        "time_created": time.time(),
    }

    database["message_id_head"] += 1

    return {"message_id": message_id}



def message_remove(token, message_id):
    """
    Given a message_id for a message, this message is removed from the channel
    """
    # Check token is valid
    if token not in database["active_tokens"]:
        raise AccessError

    # Check message exists in database
    message_exists = 0
    for ch in database["channels"].values():
        print(ch)
        for m in ch['messages'].values():
            if m["message_id"] == message_id:
                message_exists = 1

    if message_exists == 0:
        raise InputError

    # Get list of channels that the user is a part of
    user_id = auth_get_current_user_id_from_token(token)
    user_channel_id_list = [x["channel_id"] for x in channels_list(token)]

    # Remove message if user is authorised
    for ch in user_channel_id_list:
        for msg in database["channels"][ch].values()["messages"].values():
            if msg["message_id"] == message_id and (
                msg["u_id"] == user_id or (user_id in database['channels'][ch]["owner_members_id"].values())
            ):
                del msg
                return {}

    # Unauthorised to remove message
    raise AccessError


def message_edit(token, message_id, message):
    return {}
