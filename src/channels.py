from database import database
from channel import channel_details
from auth import auth_get_user_data_from_id, auth_get_current_user_id_from_token
from error import AccessError, InputError


def get_channel_id_and_name(channel):
    return {
        "channel_id": channel["id"],
        "name": channel["name"],
    }


def channels_list(token):
    channels = []
    current_user_id = auth_get_current_user_id_from_token(token)

    for channel in database["channels"].values():
        if current_user_id in channel["all_members_id"]:
            channel_info = get_channel_id_and_name(channel)
            channels.append(channel_info)

    return {"channels": channels}


def channels_listall(token):
    channels = []
    # makes sure the user is valid
    auth_get_current_user_id_from_token(token)

    for channel in database["channels"].values():
        channel_info = get_channel_id_and_name(channel)
        channels.append(channel_info)

    return {"channels": channels}


def channels_create(token, name, is_public):
    if len(name) > 20:
        raise InputError(f"{name!r} is more than 20 characters long")

    if name == "":
        name = "new_channel"

    creator_data = auth_get_user_data_from_id(
        auth_get_current_user_id_from_token(token)
    )

    id = database["channels_id_head"]
    new_channel = {
        "id": id,
        "name": name,
        "is_public": is_public,
        "owner_members_id": [creator_data["id"]],
        "all_members_id": [creator_data["id"]],
        "messages": {},
        "standup_queue": [],
        "standup_is_active": False,
        "standup_finish_time": None,
    }
    database["channels"][id] = new_channel
    database["channels_id_head"] += 1

    return {"channel_id": new_channel["id"]}
