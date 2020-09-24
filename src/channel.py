from database import data
from errors import InputError


def channel_invite(token, channel_id, u_id):
    return {}


def channel_details(token, channel_id):
    if channel_id not in data[KEY_CHANNELS]:
        raise InputError("invalid channel id")

    current_user = auth_get_current_user_from_token(token)

    if current_user[KEY_USER_ID] not in channel[KEY_CHANNEL_MEMBERS]:
        raise AccessError("not authorized to access this channel")

    channel = data[KEY_CHANNELS]
    owners = []
    for ownerid in channel[KEY_CHANNEL_OWNER]:
        owners.append(auth_get_user_details_from_id(ownerid))

    members = []
    for memberid in channel[KEY_CHANNEL_MEMBERS]:
        members.append(auth_get_user_details_from_id(memberid))

    return {
        "name": channel[KEY_CHANNEL_NAME],
        "owner_members": owners,
        "all_members": all_members,
    }


def channel_messages(token, channel_id, start):
    return {
        "messages": [
            {
                "message_id": 1,
                "u_id": 1,
                "message": "Hello world",
                "time_created": 1582426789,
            }
        ],
        "start": 0,
        "end": 50,
    }


def channel_leave(token, channel_id):
    return {}


def channel_join(token, channel_id):
    return {}


def channel_addowner(token, channel_id, u_id):
    return {}


def channel_removeowner(token, channel_id, u_id):
    return {}
