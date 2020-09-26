from database import database
from error import InputError

def channels_list(token):
    channels = []
    # TODO: Find a way to determine the user from the token
    # and use the token to determine which channels are authorised for the user.
    # at the moment, assume user_id == token

    # For every existing channel:
    for channel in database['channels']:
        # Check if the token is valid for the channel
        # add if valid
        for user in channel['owner_members_id']:
            if token == user:
                channels.append(channel)
        for user in channel['all_members_id']:
            if token == user:
                channels.append(channel)
        
    return channels

def channels_listall(token):
    channels = []
    for channel in database['channels']:
        channels.append(channel)
    return channels

def channels_create(token, name, is_public):
    if len(name) > 20:
        raise InputError(f'{name!r} is more than 20 characters long')
    channel_num = len(database['channels'])
    new_channel = {
        'name': name,
        'id': channel_num,
        'is_public': is_public,
    }
    database['channels'].append(new_channel)
    return {
        'channel_id': new_channel['id']
    }
