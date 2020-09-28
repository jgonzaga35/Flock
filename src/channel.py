from database import database
from auth import auth_get_current_user_id_from_token, auth_get_user_data_from_id
from error import InputError, AccessError


def channel_invite(token, channel_id, u_id):
    return {}


def channel_details(token, channel_id):
    current_user_id = auth_get_current_user_id_from_token(token)

    # TODO: maybe database['channels'] should be a dict and not a list
    channel = None
    for ch in database['channels']:
        if ch['id'] == channel_id:
            channel = ch

    if channel is None:
        raise InputError(f"{channel_id} is invalid channel")

    if current_user_id not in channel['all_members_id']:
        raise AccessError(f"user {current_user_id} not authorized to access this channel")

    # build the information dictionnary

    owners = []
    for ownerid in channel['owner_members_id']:
        user_data = auth_get_user_data_from_id(ownerid)
        owners.append(formated_user_details_from_user_data(user_data))

    members = []
    for memberid in channel['all_members_id']:
        user_data = auth_get_user_data_from_id(memberid)
        members.append(formated_user_details_from_user_data(user_data))

    return {
        "name": channel['name'],
        "owner_members": owners,
        "all_members": members,
    }

# Note this function assumes that channel id corressponds to their
# index in the database
def channel_messages(token, channel_id, start):
    # Invalid channel ID
    channel_total = len(database['channels'])
    if channel_id < 0 or channel_total < channel_id:
        raise InputError
    
    # Authorised user not part of channel
    current_user_id = auth_get_current_user_id_from_token(token)
    if current_user_id not in database['channels'][channel_id]['all_members_id']:
        raise AccessError
    
    # Invalid start:
    #   Negative start index
    #   Start greater than total number of messages in channel
    messages_total = len(database['channels'][channel_id]['messages'])
    if start < 0 or start > messages_total:
        raise InputError
    elif messages_total < 50:
        return -1

    channel_msg = []
    i = start
    while i < start + 50:
        message = database['channels'][channel_id]['messages']
        channel_msg.append(message)
    
    return {
        'messages': channel_msg,
        'start': start, 
        'end': start + 50,
    }

def channel_leave(token, channel_id):
    return {}


def channel_join(token, channel_id):
    return {}


def channel_addowner(token, channel_id, u_id):
    return {}


def channel_removeowner(token, channel_id, u_id):
    return {}

# helper used by channel_create
def formated_user_details_from_user_data(user_data):
    return {
        'u_id': user_data['id'],
        'name_first': user_data['first_name'],
        'name_last': user_data['last_name']
    }
