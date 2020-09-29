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
    # Invalid channel ID
    channel_total = len(database['channels'])
    if channel_id < 0 or channel_total < channel_id:
        raise InputError(f'Invalid channel_id: {channel_id}')
    
    # Authorised user not part of channel
    current_user_id = auth_get_current_user_id_from_token(token)
    if current_user_id not in database['channels'][channel_id]['all_members_id']:
        raise AccessError(f'Authorised user ({current_user_id}) not part of channel ({channel_id})')
    
    # Invalid start:
    #   Negative start index
    #   Start greater than total number of messages in channel
    messages_total = len(database['channels'][channel_id]['messages'])
    if start < 0 or start > messages_total:
        raise InputError(f'Invalid start value')

    channel_msg = [] # List of channel_messages to be returned
    end = start + 50 # Correct value unless start + 50 overflows latest message
    message_count = 0
    for message in database['channels'][channel_id]['messages']:
        # Searches database and add messages to channel_msg list
        channel_msg.append(message)
        message_count += 1
        if message_count == 50:
            break
    
    # less than 50 messages from start value to latest message
    if message_count < 50:
        end = -1
    
    return {
        'messages': channel_msg,
        'start': start, 
        'end': end,
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


# Helper function

# Eastimate whether channel is in the database
def is_channel_in_database(channel_id, channels):
    is_channel_exist = False
    for channel in channels:
        if channel['id'] == channel_id:
            is_channel_exist = True
    return is_channel_exist
