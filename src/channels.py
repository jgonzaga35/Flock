from database import database
from auth import auth_get_user_data_from_id, auth_get_current_user_id_from_token
from error import InputError

def channels_list(token):
    channels = []
    for channel in database['channels']:
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

    creator_data = auth_get_user_data_from_id(auth_get_current_user_id_from_token(token))

    channel_num = len(database['channels'])
    new_channel = {
        'name': name,
        'id': channel_num,
        'is_public': is_public,
        'owner_members_id': [creator_data['id']],
        'all_members_id': [creator_data['id']],
    }

    database['channels'].append(new_channel)

    return {
        'channel_id': new_channel['id']
    }
