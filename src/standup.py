from auth import auth_get_current_user_id_from_token, auth_get_user_data_from_id
from channel import get_channel_from_id
from database import database

from error import AccessError, InputError

from time import time
from threading import Timer


def standup_start(token, channel_id, length):
    assert length >= 0

    # Check token and chanel_id are valid
    user_id = auth_get_current_user_id_from_token(token)
    channel = get_channel_from_id(channel_id)

    # Check if a standup is already running
    if channel["standup_is_active"] == True:
        raise InputError("There's an active standup running in this channel")

    # Turn the standup on, set the time when it ends
    channel["standup_is_active"] = True
    channel["standup_finish_time"] = round(time() + length)

    # Send all message from the queue after length second
    t = Timer(length, send_message_from_queue, [user_id, channel])
    t.start()

    return {"time_finish": channel["standup_finish_time"]}


def standup_active(token, channel_id):
    # Check chanel_id is valid
    channel = get_channel_from_id(channel_id)

    time_finish = channel["standup_finish_time"]

    return {
        "is_active": channel["standup_is_active"],
        "time_finish": None if time_finish == None else time_finish,
    }


def standup_send(token, channel_id, message):
    # Check token and chanel_id are valid
    user_id = auth_get_current_user_id_from_token(token)
    channel = get_channel_from_id(channel_id)
    handle = auth_get_user_data_from_id(user_id)["handle"]

    # Check is standup is active
    if channel["standup_is_active"] == False:
        raise InputError("There's no active standup running in this channel")

    # Check is the message is too long
    if len(message) > 1000:
        raise InputError(
            f"No one is going to read a {len(message)} character long message!"
        )

    # Make the user is a memeber of the channel
    if user_id not in channel["all_members_id"]:
        raise AccessError(
            f"user {user_id} needs to be a member of this channel to send a message during standup"
        )

    # Append handle and message tuple to the list in order
    channel["standup_queue"].append((handle, message))

    return {}


# Helper function to extract messsages from standup_queue and post them
def send_message_from_queue(user_id, channel):
    # If there's any message to send
    if len(channel["standup_queue"]) != 0:
        # Compose the message from the queue
        messages = ""
        for (handle, message) in channel["standup_queue"]:
            messages = messages + handle + ": " + message + "\n"

        # Remove the last \n character
        messages = messages[:-1]

        # Add the message to the dictionary
        message_id = database["messages_id_head"]

        channel["messages"][message_id] = {
            "message_id": message_id,
            "u_id": user_id,
            "message": messages,
            "time_created": channel["standup_finish_time"],
            "is_pinned": False,
        }

        database["messages_id_head"] += 1

    # Reset the state of the variables
    channel["standup_queue"].clear()
    channel["standup_is_active"] = False
    channel["standup_finish_time"] = None
