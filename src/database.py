database = {
    'users': [],
    'channels': [],
    'active_tokens': []
}

def clear_database():
    database['users'].clear()
    database['channels'].clear()
    database['active_tokens'].clear()