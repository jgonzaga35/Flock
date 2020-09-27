from database import database
from channel import channel_details,formated_user_details_from_user_data
from auth import auth_get_user_data_from_id, auth_get_current_user_id_from_token
from error import InputError

def channels_list(token):
    channels = []
    current_user_id = auth_get_current_user_id_from_token(token)
    for channel in database['channels']:
        for user_id in channel['all_members_id']:
            if current_user_id == user_id: 
                channels.append(channel_details(token, channel['id']))
    return channels

def channels_listall(token):
    #TODO: this function should return a list of all channels
    # regardless of permissions. How to do this with tokens?? not sure...
    channels = []
    for channel in database['channels']:
        # Assuming that token = user_id, this picks the first user_id in
        # the channel so that channel_details() is always passed an authorised token
        authorised_token = channel['all_members_id'][0]

        channels.append(channel_details(authorised_token, channel['id']))
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
