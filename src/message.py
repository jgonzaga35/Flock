from database import database
from auth import auth_get_current_user_id_from_token
from channel import get_channel_from_id
from channels import channels_list

import time
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
    """
    Given a message_id for a message, this message is removed from the channel
    """
    # Check token is valid - error checking in function
    user_id = auth_get_current_user_id_from_token(token)

    # Check message exists in database
    message_exists = False
    for ch in database["channels"].values():
        if message_id in ch["messages"]:
            channel_id_for_message = ch["id"]
            message_exists = True

    if message_exists == False:
        raise InputError

    if (
        database["users"][user_id]["is_admin"] is False
        and user_id
        not in database["channels"][channel_id_for_message]["all_members_id"]
    ):
        raise AccessError(
            "user must be part of the channel to remove his/her message (see assumptions.md)"
        )

    # Remove message if user is authorised
    for msg in database["channels"][channel_id_for_message]["messages"].values():
        if msg["message_id"] == message_id and (
            msg["u_id"] == user_id
            or (
                user_id
                in database["channels"][channel_id_for_message]["owner_members_id"]
            )
            or database["users"][user_id]["is_admin"]
        ):
            del database["channels"][channel_id_for_message]["messages"][message_id]
            return {}

    # Unauthorised to remove message
    raise AccessError


def message_edit(token, message_id, message):
    """Given a message, update its text with new text. If the new message
    is an empty string, the message is deleted
    """

    # Check token is valid - error checking in function
    user_id = auth_get_current_user_id_from_token(token)

    # Check message exists in database
    message_exists = False
    for ch in database["channels"].values():
        if message_id in ch["messages"]:
            channel_id_for_message = ch["id"]
            message_exists = True

    if message_exists == False:
        raise AccessError

    if (
        database["users"][user_id]["is_admin"] is False
        and user_id
        not in database["channels"][channel_id_for_message]["all_members_id"]
    ):
        raise AccessError(
            "user must be part of the channel to edit his/her message (see assumptions.md)"
        )

    # This is done after error checking as input error not allowed in this function
    if message == "":
        message_remove(token, message_id)
        return {}

    if len(message) > 1000:
        raise InputError("message cannot exceed 1000 characters (see assumptions.md)")

    # Edit message if user is authorised, delete if message = ''
    for msg in database["channels"][channel_id_for_message]["messages"].values():
        if msg["message_id"] == message_id and (
            msg["u_id"] == user_id
            or (
                user_id
                in database["channels"][channel_id_for_message]["owner_members_id"]
            )
            or (database["users"][user_id]["is_admin"])
        ):
            msg["message"] = message
            return {}

    # Unauthorised to edit message
    raise AccessError
