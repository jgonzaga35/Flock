from database import database
from error import AccessError, InputError
def channel_invite(token, channel_id, u_id):
    return {
    }

def channel_details(token, channel_id):
    return {
        'name': 'Hayden',
        'owner_members': [
            {
                'u_id': 1,
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
            }
        ],
        'all_members': [
            {
                'u_id': 1,
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
            }
        ],
    }

def channel_messages(token, channel_id, start):
    return {
        'messages': [
            {
                'message_id': 1,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
            }
        ],
        'start': 0,
        'end': 50,
    }

def channel_leave(token, channel_id):

    if channel_id not in range(len(database['channels'])):
        raise InputError('Channel ID is invalid')

    if token not in database['channels'][channel_id]['user_list']:
        raise AccessError('User is not in this channel')
    
    #Delete the user's token from that channel
    for user in database['channels'][channel_id]['user_list']:
        if token == user:
           database['channels'][channel_id]['user_list'].remove(token)

def channel_join(token, channel_id):
    if channel_id not in range(len(database['channels'])):
        raise InputError('Channel ID is invalid')
    
    if token not in database['active_tokens']:
        raise AccessError('Token is not activated')

    if not database['channels'][channel_id]['is_public']:
        raise AccessError('Channels is not public')
    
    database['channels'][channel_id]['user_list'].append(token)

def channel_addowner(token, channel_id, u_id):
    return {
    }

def channel_removeowner(token, channel_id, u_id):
    return {
    }


# Helper function

# Eastimate whether channel is in the database
def is_channel_in_database(channel_id, channels):
    is_channel_exist = False
    for channel in channels:
        if channel['id'] == channel_id:
            is_channel_exist = True
    return is_channel_exist