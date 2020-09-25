from database import database
from error import InputError


def channel_invite(token, channel_id, u_id):
    return {}


def channel_details(token, channel_id):
    if channel_id not in database['channels']:
        raise InputError(f"{channel_id} is invalid channel id")

    current_user_id = auth_get_current_user_id_from_token(token)

    if current_user['id'] not in channel['members']:
        raise AccessError("not authorized to access this channel")

    channel = database['channels']
    owners = []
    for ownerid in channel['ownersid']:
        owners.append(auth_get_user_details_from_id(ownerid))

    members = []
    for memberid in channel['membersid']:
        members.append(auth_get_user_details_from_id(memberid))

    return {
        "name": channel['name'],
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
