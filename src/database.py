database = {
    "users": {},
    "users_id_head": 1,
    # id_heads are only ever incremented, they are used to generate ids
    "channels_id_head": 1,
    "channels": {
        # id: {
        #     "id": 1,
        #     "name": "greatest_channel",
        #     # the user id of the owners
        #     "owner_members_id": [1, 2, 3]
        #     # the user id of all the members (including the owners)
        #     "all_members_id": [1, 2, 3, 5, 4, 9]
        #     "is_public": True
        #      "messages": [
        #           {
        #               "message_id": 1,
        #               "u_id": 1,
        #               "message": "Hello world",
        #               "time_created": 1582426789,
        #           }
        #       ],
        # },
    },
    "active_tokens": [],
}


def clear_database():
    database["users"].clear()
    database["channels"].clear()
    database["active_tokens"].clear()
