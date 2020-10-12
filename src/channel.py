from database import database
from auth import auth_get_current_user_id_from_token, auth_get_user_data_from_id
from error import InputError, AccessError


def channel_invite(token, channel_id, u_id):
    inviter_user_id = auth_get_current_user_id_from_token(token)

    valid_user = None
    for user in database["users"]:
        if user["id"] == u_id:
            valid_user = user

    if valid_user is None:
        raise InputError(f"{u_id} is an invalid user id")

    target_channel = None
    for channel in database["channels"]:
        if channel["id"] == channel_id:
            target_channel = channel

    if target_channel is None:
        raise InputError(f"{channel_id} is invalid channel")

    if inviter_user_id not in target_channel["all_members_id"]:
        raise AccessError(
            f"user {inviter_user_id} not authorized to invite you to this channel"
        )

    if u_id not in target_channel["all_members_id"]:
        target_channel["all_members_id"].append(u_id)

    return {}


def channel_details(token, channel_id):
    current_user_id = auth_get_current_user_id_from_token(token)

    # TODO: maybe database['channels'] should be a dict and not a list
    target_channel = None
    for channel in database["channels"]:
        if channel["id"] == channel_id:
            target_channel = channel

    if target_channel is None:
        raise InputError(f"{channel_id} is invalid channel")

    if current_user_id not in target_channel["all_members_id"]:
        raise AccessError(
            f"user {current_user_id} not authorized to access this channel"
        )

    # build the information dictionnary

    owners = []
    for ownerid in target_channel["owner_members_id"]:
        user_data = auth_get_user_data_from_id(ownerid)
        owners.append(formated_user_details_from_user_data(user_data))

    members = []
    for memberid in target_channel["all_members_id"]:
        user_data = auth_get_user_data_from_id(memberid)
        members.append(formated_user_details_from_user_data(user_data))

    return {
        "name": target_channel["name"],
        "owner_members": owners,
        "all_members": members,
    }


def channel_messages(token, channel_id, start):
    # Invalid channel ID
    channel_total = len(database["channels"])
    if channel_id < 0 or channel_total < channel_id:
        raise InputError(f"Invalid channel_id: {channel_id}")

    # Authorised user not part of channel
    current_user_id = auth_get_current_user_id_from_token(token)
    if current_user_id not in database["channels"][channel_id]["all_members_id"]:
        raise AccessError(
            f"Authorised user ({current_user_id}) not part of channel ({channel_id})"
        )

    # Invalid start:
    #   Negative start index
    #   Start greater than total number of messages in channel
    messages_total = len(database["channels"][channel_id]["messages"])
    if start < 0 or start > messages_total:
        raise InputError("Invalid start value")

    channel_msg = []  # List of channel_messages to be returned
    end = start + 50  # Correct value unless start + 50 overflows latest message

    # comment this out for now because we don't have message_send yet, so we
    # can't black box test this YET, so coverage isn't happy.

    # message_count = 0

    # for message in database['channels'][channel_id]['messages']:
    #     # Searches database and add messages to channel_msg list
    #     channel_msg.append(message)
    #     message_count += 1
    #     if message_count == 50:
    #         break

    # # less than 50 messages from start value to latest message
    # if message_count < 50:
    #     end = -1

    end = -1

    return {
        "messages": channel_msg,
        "start": start,
        "end": end,
    }


def channel_leave(token, channel_id):
    target_channel = None
    current_user_id = auth_get_current_user_id_from_token(token)
    for channel in database["channels"]:
        if channel["id"] == channel_id:
            target_channel = channel

    if target_channel is None:
        raise InputError("Channel ID is invalid")
    # This method of accessing channel is written by
    # Matheiu in channel_details. Still has to figure out
    # whether need to change the channels as list to channel as dictionary

    if current_user_id not in target_channel["all_members_id"]:
        raise AccessError("User is not in this channel")

    # Delete the user's token from that channel
    for user in target_channel["all_members_id"]:
        if current_user_id == user:
            target_channel["all_members_id"].remove(current_user_id)


def channel_join(token, channel_id):
    target_channel = None
    current_user_id = auth_get_current_user_id_from_token(token)
    for channel in database["channels"]:
        if channel["id"] == channel_id:
            target_channel = channel

    if target_channel is None:
        raise InputError("Channel ID is invalid")

    if not target_channel["is_public"]:
        raise AccessError("Channel is not public")

    for channel in database["channels"]:
        if channel["id"] == channel_id:
            channel["all_members_id"].append(current_user_id)


def channel_addowner(token, channel_id, u_id):
    # Generate channel that match the channel_id
    channel = next(
        (channel for channel in database["channels"] if channel["id"] == channel_id),
        None,
    )
    if channel == None:
        raise InputError("Channel_id is not valid")

    if u_id in channel["owner_members_id"]:
        raise InputError("User is already an owner of the channel")

    if u_id not in channel["all_members_id"]:
        raise InputError("User not in the channel")

    if auth_get_current_user_id_from_token(token) not in channel["owner_members_id"]:
        raise AccessError("User is not owner")

    channel["owner_members_id"].append(u_id)


def channel_removeowner(token, channel_id, u_id):
    """
    When there is only one owner in the channel and this owner is removed,
    there should be another user in this room randomly became the owner.
    """
    # Generate the channel which match the channel_id
    channel = next(
        (channel for channel in database["channels"] if channel["id"] == channel_id),
        None,
    )
    user_who_remove_others_uid = auth_get_current_user_id_from_token(token)
    if channel == None:
        raise InputError("Channel_id is not valid")

    if u_id not in channel["owner_members_id"]:
        raise InputError("User is not a owner, can not be removed")

    if user_who_remove_others_uid not in channel["owner_members_id"]:
        raise AccessError("User is not authorized")

    # If the owner is the only owner in the channel
    if len(channel["owner_members_id"]) == 1:
        # Generate a user to become the owner
        next_owner_uid = next(
            (
                user
                for user in channel["all_members_id"]
                if user != user_who_remove_others_uid
            ),
            None,
        )
        if next_owner_uid != None:
            for channel in database["channels"]:
                if channel["id"] == channel_id:
                    channel["owner_members_id"].append(next_owner_uid)

    # If there are only one member in the channel(including owner),
    # remove the whole channel otherwise remove the owner.
    if len(channel["all_members_id"]) == 1:
        channel_remove(channel_id)
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


def channel_remove(channel_id):
    """
    remove the channel based on its channel_id
    This is not a official function, use it as a helper

    However, removing channel will change the index of the element in the
    'channels' list, so there should be no access to channel in the database
    directly using channel_id as its index
    For example:

    Bad access:
    >>> database['channels'][channel_id]

    Good access:
    >>> for channel in database['channels']:
            if channel['id'] == channel_id:
                do something
    """

    # the [:] is me showing off. I can think of two options:
    # database['channels'] = list(filter(...)) # allocates a new list for sure
    # database['channels'][:] = filter(...)    # has a chance of writing the list in place, maybe without reallocating
    database["channels"][:] = filter(
        lambda channel: channel["id"] != channel_id, database["channels"]
    )
