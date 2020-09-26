database = {
    'users': [],
    'channels': [
        # {
        #     "id": 1,
        #     "name": "greatest_channel",
        #     # the user id of the owners
        #     "owner_members_id": [1, 2, 3]
        #     # the user id of all the members (including the owners)
        #     "all_members_id": [1, 2, 3, 5, 4, 9]
        #     "is_public": True
        # },
        # {
        #     "id": 2,
        #     "name": "me myself and I",
        #     "owner_members_id": [3]
        #     "all_members_id": [3]
        #     "is_public": False
        # }
    ],
    'active_tokens': []
}

def clear_database():
    database['users'].clear()
    database['channels'].clear()
    database['active_tokens'].clear()