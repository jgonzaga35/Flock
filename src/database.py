database = {
    "users": {},
    "users_id_head": 1,
    # id_heads are only ever incremented, they are used to generate ids
    "channels_id_head": 1,
    "channels": {
        # 1: {
        #     "id": 1,
        #     "name": "greatest_channel",
        #     # the user id of the owners
        #     "owner_members_id": [1, 2, 3]
        #     # the user id of all the members (including the owners)
        #     "all_members_id": [1, 2, 3, 5, 4, 9]
        #     "is_public": True,
        #     "is_admin": False, # is a global "flockr owner"
        #     "messages": {
        #           1: {
        #               "message_id": 1,
        #               "u_id": 1,
        #               "message": "Hello world",
        #               "time_created": 1582426789,
        #               "is_pinned": False,
        #               "reacts": [
        #                           { "react_id" : 1,
        #                                "u_ids": [1, 2, 3, 4],
        #                           },
        #                         ]
        #
        #           }
        #       },
        # },
    },
    # no message should have the same id, even across channels
    "messages_id_head": 1,
    "active_tokens": [],
}
