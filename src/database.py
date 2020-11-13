database = {
    "users": {
        # u_id: {
        #     "email": email,
        #     "password": encrypt(password),
        #     "first_name": name_first,
        #     "last_name": name_last,
        #     "id": u_id,
        #     "handle": String,
        #     "is_admin": Bool,
        # }
    },
    "users_id_head": 1,
    # id_heads are only ever incremented, they are used to generate ids
    "channels_id_head": 1,
    "channels": {
        # 1: {
        #     "id": 1,
        #     "name": "greatest_channel",
        #     # the user id of the owners
        #     "owner_members_id": [1, 2, 3],
        #     # the user id of all the members (including the owners)
        #     "all_members_id": [1, 2, 3, 5, 4, 9],
        #     "is_public": True,
        #     "is_admin": False, # is a global "flockr owner"
        #     "messages": {
        #           1: {
        #               "message_id": 1,
        #               "u_id": 1,
        #               "message": "Hello world",
        #               "time_created": 1582426789,
        #               "is_pinned": False,
        #           }
        #       },
        #     "standup_queue": [
        #             (handle, message)
        #         ],
        #     "standup_is_active": True,
        #     "standup_finish_time": None
        # },
    },
    # no message should have the same id, even across channels
    "messages_id_head": 1,
    "active_tokens": [],
}
