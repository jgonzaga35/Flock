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
    channel = None
    current_user_id = auth_get_current_user_id_from_token(token)
    for ch in database['channels']:
        if ch['id'] == channel_id:
            channel = ch

    if channel is None:
        raise InputError('Channel ID is invalid') # This method of accessing channel is written by
                                                  # Matheiu in channel_details. Still has to figure out
                                                  # whether need to change the channels as list to channel as dictionary

    if current_user_id not in channel['all_members_id']:
        raise AccessError('User is not in this channel')
    
    #Delete the user's token from that channel
    for user in channel['all_members_id']:
        if current_user_id == user:
           channel['all_members_id'].remove(current_user_id)

def channel_join(token, channel_id):
    channel = None
    current_user_id = auth_get_current_user_id_from_token(token)
    for ch in database['channels']:
        if ch['id'] == channel_id:
            channel = ch

    if channel is None:
        raise InputError('Channel ID is invalid') 
    
    if token not in database['active_tokens']:
        raise AccessError('Token is not activated')

    if not channel['is_public']:
        raise AccessError('Channel is not public')
    
    for ch in database['channels']:
        if ch['id'] == channel_id:
            ch['all_members_id'].append(current_user_id)

def channel_addowner(token, channel_id, u_id):
    # Generate channel that match the channel_id
    channel =  next((channel for channel in database['channels'] if channel["id"] == channel_id), None)
    if (channel == None):
        raise InputError("Channel_id is not valid")
    
    if u_id in channel['owner_members_id']:
        raise InputError("Channel is already in the channel")
    
    if u_id not in channel['all_members_id']:
        raise InputError("User not in the channel")

    if auth_get_current_user_id_from_token(token) not in channel['owner_members_id']:
        raise AccessError("User is not owner")

    for channel in database['channels']:
        if channel['id'] == channel_id:
            channel['owner_members_id'].append(u_id)


def channel_removeowner(token, channel_id, u_id):
    return {}

# helper used by channel_create
def formated_user_details_from_user_data(user_data):
    return {
        'u_id': user_data['id'],
        'name_first': user_data['first_name'],
        'name_last': user_data['last_name']
    }


# Helper function

# Eastimate whether channel is in the database
def is_channel_in_database(channel_id, channels):
    is_channel_exist = False
    for channel in channels:
        if channel['id'] == channel_id:
            is_channel_exist = True
    return is_channel_exist
