from database import database
from auth import auth_get_current_user_id_from_token
from channels import channels_list

from error import AccessError, InputError


def message_send(token, channel_id, message):
    return {
        "message_id": 1,
    }


def message_remove(token, message_id):
    """
    Given a message_id for a message, this message is removed from the channel
    """
    # Check token is valid
    if token not in database["active_tokens"]:
        raise AccessError

    # Check message exists in database
    message_exists = 0
    for ch in database["channels"]:
        for m in ch['messages']:
            if m["message_id"] == message_id:
                message_exists = 1

    if message_exists == 0:
        raise InputError

    # Get list of channels that the user is a part of
    user_id = auth_get_current_user_id_from_token(token)
    channels_user_is_in = channels_list(token)
    user_channel_id_list = [
        channels_user_is_in["channel_id"] for x in channels_user_is_in
    ]

    for ch in user_channel_id_list:
        for msg in database["channels"][ch]["messages"]:
            if msg["message_id"] == message_id and (
                msg["u_id"] == user_id or (user_id in database['channels'][ch]["owner_members_id"])
            ):
                del msg
                return {}

    # Message exists but not sent by this user or user trying to remove a
    # message they are not authorised to remove
    raise AccessError


def message_edit(token, message_id, message):
    return {}
