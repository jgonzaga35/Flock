import sys
from json import dumps
from flask import Flask, request, jsonify
from flask_cors import CORS
from error import InputError
from auth import auth_login, auth_logout, auth_register
from other import clear
from message import message_send, message_edit, message_remove
from channel import channel_join, channel_messages, channel_details
from channels import channels_create


def defaultHandler(err):
    response = err.get_response()
    print("response", err, err.get_response())
    response.data = dumps(
        {
            "code": err.code,
            "name": "System Error",
            "message": err.get_description(),
        }
    )
    response.content_type = "application/json"
    return response


APP = Flask(__name__)
CORS(APP)

APP.config["TRAP_HTTP_EXCEPTIONS"] = True
APP.register_error_handler(Exception, defaultHandler)

# Example
@APP.route("/echo", methods=["GET"])
def echo():
    data = request.args.get("data")
    if data == "echo":
        raise InputError(description='Cannot echo "echo"')
    return dumps({"data": data})


@APP.route("/clear", methods=["DELETE"])
def delete():
    clear()
    return dumps({})


# Auth_functions
@APP.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    return dumps(auth_login(data["email"], data["password"]))


@APP.route("/auth/logout", methods=["POST"])
def logout():
    data = request.get_json()
    return dumps(auth_logout(data["token"]))


@APP.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    return dumps(
        auth_register(
            data["email"], data["password"], data["name_first"], data["name_last"]
        )
    )

#############################################################################
#                           Routes for messages                             #
#############################################################################
@APP.route("/channels/create", methods=["POST"])
def channels_create_handler():
    data = request.get_json()

    token = data["token"]
    name = data["name"]
    is_public = data["is_public"]
    
    return jsonify(channels_create(token, name, is_public))

@APP.route("/message/send", methods=["POST"])
def send_message():
    data = request.get_json()

    token = data["token"]
    channel_id = data["channel_id"]
    message = data["message"]

    return jsonify(message_send(token, channel_id, message))

@APP.route("/channel/join", methods=["POST"])
def join_channel():
    data = request.get_json()

    token = data["token"]
    channel_id = data["channel_id"]
    channel_join(token, channel_id)
    return dumps({})

# Last test fails with this route if int() is included
@APP.route("/channel/messages", methods=["GET"])
def messages_channel():
    token = (request.args.get("token"))
    channel_id = request.args.get("channel_id")
    start = request.args.get("start")

    return dumps({
        channel_messages(int(token), int(channel_id), int(start))
    })

@APP.route("/message/edit", methods=["PUT"])
def edit_message():
    data = request.get_json()
    message_edit(data["token"], data["message_id"], data["message"])
    return dumps({})
    
@APP.route("/channels/create", methods=["POST"])
def channels_create_handler():
    data = request.get_json()

    token = data["token"]
    name = data["name"]
    is_public = data["is_public"]

    return jsonify(channels_create(token, name, is_public))


@APP.route("/channel/details", methods=["GET"])
def channel_details_handler():
    token = int(request.args.get("token"))
    channel_id = int(request.args.get("channel_id"))
    return jsonify(channel_details(token, channel_id))


if __name__ == "__main__":
    APP.run(port=0)  # Do not edit this port
