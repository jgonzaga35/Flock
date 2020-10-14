from database import database

def message_send(token, channel_id, message):
    return {
        "message_id": 1,
    }


def message_remove(token, message_id):
    '''
        Given a message_id for a message, this message is removed from the channel
    '''
    return {}


def message_edit(token, message_id, message):
    return {}
