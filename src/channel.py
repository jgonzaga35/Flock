from database import database
from auth import auth_get_current_user_id_from_token, auth_get_user_data_from_id
from error import InputError, AccessError


def channel_invite(token, channel_id, u_id):
    inviter_user_id = auth_get_current_user_id_from_token(token)

    try:
        database["users"][u_id]
    except KeyError:
        raise InputError(f"{u_id} is an invalid user id")

    channel = get_channel_from_id(channel_id)

    if inviter_user_id not in channel["all_members_id"]:
        raise AccessError(
            f"user {inviter_user_id} not authorized to invite you to this channel"
        )

    if u_id not in channel["all_members_id"]:
        channel["all_members_id"].append(u_id)

    return {}


def channel_details(token, channel_id):
    """
    Return channel_details with formats below:
    >>>
    {
        "name": channel["name"],
        "owner_members": owners,
        "all_members": members,
    }
    """
    current_user_id = auth_get_current_user_id_from_token(token)

    channel = get_channel_from_id(channel_id)

    if current_user_id not in channel["all_members_id"]:
        raise AccessError(
            f"user {current_user_id} not authorized to access this channel"
        )

    # build the information dictionnary

    owners = []
    for ownerid in channel["owner_members_id"]:
        user_data = auth_get_user_data_from_id(ownerid)
        owners.append(formated_user_details_from_user_data(user_data))

    members = []
    for memberid in channel["all_members_id"]:
        user_data = auth_get_user_data_from_id(memberid)
        members.append(formated_user_details_from_user_data(user_data))

    return {
        "name": channel["name"],
        "owner_members": owners,
        "all_members": members,
    }


def channel_messages(token, channel_id, start):
    current_user_id = auth_get_current_user_id_from_token(token)
    channel = get_channel_from_id(channel_id)

    # Authorised user not part of channel
    if current_user_id not in channel["all_members_id"]:
        raise AccessError(
            f"Authorised user ({current_user_id}) not part of channel ({channel_id})"
        )

    # Invalid start:
    #   Negative start index
    #   Start greater than total number of messages in channel
    messages_total = len(channel["messages"])
    if start < 0 or start > messages_total:
        raise InputError("Invalid start value")

    # some unreadable-smart-looking python code to make please my ego. sorted
    # sorts each messages according to the "time_created" key we reverse
    # because we want the newest message first (newer means bigger timestamp)
    # then, [start:start+50] takes a slice of a list. start is included,
    # start+50 is excluded, so it gives exactly 50 elements at most. If
    # start+50 >= len(messages), then python handles everything nicely and just
    # gives back a smaller slice.
    channel_messages = sorted(
        channel["messages"].values(), key=lambda msg: msg["time_created"], reverse=True
    )[start : start + 50]

    return {
        "messages": channel_messages,
        "start": start,
        # showing off again...
        "end": -1 if len(channel_messages) < 50 else start + 50,
    }


def channel_leave(token, channel_id):
    current_user_id = auth_get_current_user_id_from_token(token)
    channel = get_channel_from_id(channel_id)

    if current_user_id not in channel["all_members_id"]:
        raise AccessError("User is not in this channel")

    # If a user is owner of that channel, he should be removed
    # from the owner list when he left the channel
    if current_user_id in channel["owner_members_id"]:
        channel["owner_members_id"].remove(current_user_id)

    # Delete the user's token from that channel
    channel["all_members_id"].remove(current_user_id)


def channel_join(token, channel_id):
    current_user_id = auth_get_current_user_id_from_token(token)
    channel = get_channel_from_id(channel_id)

    if not channel["is_public"]:
        raise AccessError("Channel is not public")

    if len(channel["all_members_id"]) == 0:
        channel["owner_members_id"].append(current_user_id)

    channel["all_members_id"].append(current_user_id)


def channel_addowner(token, channel_id, u_id):
    channel = get_channel_from_id(channel_id)

    if u_id in channel["owner_members_id"]:
        raise InputError("User is already an owner of the channel")

    if auth_get_current_user_id_from_token(token) not in channel["owner_members_id"]:
        raise AccessError("User is not owner")

    if u_id in channel["all_members_id"]:
        channel["owner_members_id"].append(u_id)
    else:
        # If a user outside the channel being added owner, he will
        # first be invited to the channel, then become an owner.
        channel_invite(token, channel_id, u_id)
        channel["owner_members_id"].append(u_id)


def channel_removeowner(token, channel_id, u_id):
    """
    When there is only one owner in the channel and this owner is removed,
    there should be another user in this room randomly became the owner.
    """
    # Generate the channel which match the channel_id
    user_who_remove_others_uid = auth_get_current_user_id_from_token(token)

    channel = get_channel_from_id(channel_id)

    if u_id not in channel["owner_members_id"]:
        raise InputError("User is not a owner, can not be removed")

    if user_who_remove_others_uid not in channel["owner_members_id"]:
        raise AccessError("User is not authorized")

    # If a owner are the only member of a channel, when this owner
    # remove owner himself, he will automatically leave the channel
    if len(channel["all_members_id"]) == 1:
        channel_leave(token, channel_id)
    else:
        # If the owner is the only owner in the channel
        if len(channel["owner_members_id"]) == 1:

            # Generate a member of channel to become the owner
            owner_iterator = iter(
                [
                    user
                    for user in channel["all_members_id"]
                    if user != user_who_remove_others_uid
                ]
            )
            next_owner_uid = next(owner_iterator, None)

            # We assume we will always find a member in the channel
            # to become owner since length of channel["all_members_id"]
            # is bigger than 2
            assert next_owner_uid != None
            channel["owner_members_id"].append(next_owner_uid)
            channel["owner_members_id"].remove(u_id)
        else:
            channel["owner_members_id"].remove(u_id)


# helper used by channel_create
def formated_user_details_from_user_data(user_data):
    return {
        "u_id": user_data["id"],
        "name_first": user_data["first_name"],
        "name_last": user_data["last_name"],
    }


# Helper function


# def channel_remove(channel_id):
#     """
#     remove the channel based on its channel_id
#     This is not a official function, use it as a helper
#     """

#     del database["channels"][channel_id]


def get_channel_from_id(channel_id):
    """
    Return a channel from database based on its channel id
    """
    try:
        return database["channels"][channel_id]
    except KeyError:
        raise InputError(f"{channel_id} is an invalid channel id")
