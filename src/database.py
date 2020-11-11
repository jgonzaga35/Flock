# id_heads are only ever incremented, they are used to generate ids

database = {
    "users": {
        # {
        #     "id": 2,
        #     "email": "yo@gmail.com",
        #     "password": "<encrypted password>",
        #     "first_name": "first_name",
        #     "last_name": "last_name",
        #     "handle": "first_name_last_name",
        #     "is_admin": False,
        #     "profile_img_url": "/static/default_user_profile.png",
        # },
    },
    "users_id_head": 1,
    "channels_id_head": 1,
    "channels": {
        # 1: {
        #     "id": 1,
        #     "name": "greatest_channel",
        #     "owner_members_id": [1, 2, 3],
        #     "all_members_id": [1, 2, 3, 5, 4, 9],
        #     "is_public": True,
        #     "is_admin": False,
        #     "messages": {
        #         "1": {
        #             "message_id": 1,
        #             "u_id": 1,
        #             "message": "Hello world",
        #             "time_created": 1582426789,
        #             "is_pinned": False,
        #             "reacts": [
        #                 {
        #                     "react_id": 1,
        #                     "u_ids": [1, 2, 3, 4],
        #                 },
        #             ],
        #         }
        #     },
        # },
    },
    # no message should have the same id, even across channels
    "messages_id_head": 1,
    "active_tokens": [],
    "reset_codes_head": 1,
    "reset_codes": {},
}
