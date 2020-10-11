def message_send(token, channel_id, message):
    return {
        'message_id': 1,
    }

def message_remove(token, message_id):
    return {
    }

def message_edit(token, message_id, message):
    '''
    Given a message, update it's text with new text. 
    If the new message is an empty string, the message is deleted.
    '''
    # Check user is valid
    # Check message_id is valid
    # Check user is authorised to edit message
    return {
    }