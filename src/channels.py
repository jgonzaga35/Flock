from database import database
from error import InputError

def channels_list(token):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }

def channels_listall(token):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }

def channels_create(token, name, is_public):
    if len(name) > 20:
        raise InputError(f'{name!r} is more than 20 characters long')
    channel_num = len(database['channels'])
    new_channel = {
        'name': name,
        'id': channel_num,
        'is_public': is_public,
        'user_list': [token]
    }
    database['channels'].append(new_channel)
    return {
        'channel_id': new_channel['id']
    }
