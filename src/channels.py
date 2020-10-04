from database import database
from channel import channel_details
from auth import auth_get_user_data_from_id, auth_get_current_user_id_from_token
from error import AccessError, InputError

def simplify_channel_details(token, channel_id):
    return {
        'channel_id': channel_id,
        'name': channel_details(token, channel_id)['name']
    }

def channels_list(token):
    channels = []
    current_user_id = auth_get_current_user_id_from_token(token)

    valid_user = False
    for user in database['users']:
        if current_user_id == user['id']:
            valid_user = True
    
    if valid_user == False:
        raise AccessError(f"The token {token} is invalid")
    
    for channel in database['channels']:
        for user_id in channel['all_members_id']:
            if current_user_id == user_id:
                channels.append(simplify_channel_details(token, channel['id']))
    return channels

def channels_listall(token):
    channels = []
    current_user_id = auth_get_current_user_id_from_token(token)
    
    valid_user = False
    for user in database['users']:
        if current_user_id == user['id']:
            valid_user = True
    
    if valid_user == False:
        raise AccessError(f"The token {token} is invalid")

    for channel in database['channels']:
        authorised_token = channel['all_members_id'][0]
        channels.append(simplify_channel_details(authorised_token, channel['id']))
    return channels

def channels_create(token, name, is_public):
    if len(name) > 20:
        raise InputError(f'{name!r} is more than 20 characters long')

    if name == "":
        name = "new_channel"

    creator_data = auth_get_user_data_from_id(auth_get_current_user_id_from_token(token))

    channel_num = len(database['channels'])
    new_channel = {
        'name': name,
        'id': channel_num,
        'is_public': is_public,
        'owner_members_id': [creator_data['id']],
        'all_members_id': [creator_data['id']],
        'messages': [],
    }

    database['channels'].append(new_channel)

    return {
        'channel_id': new_channel['id']
    }
