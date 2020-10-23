import re
from database import database
from error import InputError, AccessError
import jwt
from hashlib import sha256

TOKEN_SECRET_KEY = "COMP1531_MANGO_FRI_666"  # The key to the JWT encoding


def auth_login(email, password):
    check_email(email)

    for user in database["users"].values():
        if user["email"] == email:
            if user["password"] == encrypt(password):
                u_id = user["id"]
                # Check if the user has been logged in, if so, return the same active token
                active_token = next(
                    (
                        exist_token
                        for exist_token in database["active_tokens"]
                        if auth_get_current_user_id_from_token(exist_token) == u_id
                    ),
                    None,
                )

                # If the user is not logged in, append a new token
                if active_token == None:
                    token = jwt_encode(auth_get_user_data_from_id(u_id))
                    database["active_tokens"].append(token)
                    active_token = token

                return {
                    "u_id": u_id,
                    "token": active_token,
                }

            raise InputError("Wrong password.")
    raise InputError("User doesn't exist.")


def auth_logout(token):
    if token in database["active_tokens"]:
        database["active_tokens"].remove(token)
        is_success = True
    else:
        is_success = False

    return {
        "is_success": is_success,
    }


def auth_register(email, password, name_first, name_last):
    input_error_checking(email, password, name_first, name_last)

    # Check if email is already taken
    for user in database["users"].values():
        if user["email"] == email:
            raise InputError("Email has been used.")

    # The next u_id to be used is stored in the database
    u_id = database["users_id_head"]
    new_user = {
        "email": email,
        "password": encrypt(password),
        "first_name": name_first,
        "last_name": name_last,
        "id": u_id,
        "handle": generate_handle(name_first, name_last, u_id),
        "is_admin": False,
    }

    # first user to register automatically becomes an admin (flockr owner)
    if len(database["users"]) == 0:
        new_user["is_admin"] = True

    token = jwt_encode(new_user)

    database["users"][u_id] = new_user  # Append all info under the user's u_id key
    database["users_id_head"] += 1  # Increment so that u_ids are unique
    database["active_tokens"].append(token)  # Log user in automatically

    return {
        "u_id": u_id,
        "token": token,
    }


# Helper to get u_id from token
def auth_get_current_user_id_from_token(token):
    if token not in database["active_tokens"]:
        raise AccessError("token is invalid")

    return jwt_decode(token)["id"]


# Helper to get all user data from their id
def auth_get_user_data_from_id(user_id):
    """Raises KeyError is the a user with id id doesn't exists. It should
    never happen, because only valid id should be generated from tokens"""
    return database["users"][user_id]


# Helper function for validating an Email
def check_email(email):
    regex = r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
    if re.search(regex, email):
        return
    raise InputError("Email inputted is invalid.")


# Helper function to check register info.
def input_error_checking(email, password, name_first, name_last):
    check_email(email)

    if len(password) < 6:
        raise InputError("Password is too short.")

    if len(name_first) > 50 or len(name_first) < 1:
        raise InputError("First name is invalid.")

    if len(name_last) > 50 or len(name_last) < 1:
        raise InputError("Last name is invalid.")


# Helper function that returns encoded jwt
def jwt_encode(user_info):
    return jwt.encode(user_info, TOKEN_SECRET_KEY, algorithm="HS256").decode("utf-8")


# Helper function to decode jwt
def jwt_decode(token):
    # If decode fails, we raise an AccessError
    try:
        return jwt.decode(token.encode("utf-8"), TOKEN_SECRET_KEY, algorithms=["HS256"])
    except jwt.exceptions.InvalidTokenError:
        raise AccessError("Decoding token fails")


# Helper function to generate handle for a user
def generate_handle(first_name, last_name, u_id):
    u_id = str(u_id)
    assert len(u_id) < 20

    handle = first_name.lower() + last_name.lower()
    # If the concatenation of first and last name exceeds 20, we only keep the first 20
    if len(handle) > 20:
        handle = handle[:20]

    # If the handles is taken, we add the unique u_id to the end
    if is_handle_already_used(handle):
        if len(handle) + len(u_id) > 20:
            handle = handle[: (20 - len(u_id))] + u_id
        else:
            handle = handle + u_id
    return handle


# Helper function to check whether the handle exist already
def is_handle_already_used(handle):
    # Loop through all the handles
    for user in database["users"].values():
        if user["handle"] == handle:
            return True
    return False


# Helper function to encrypt user password and return the hex representation
def encrypt(password):
    """Return the encrypted form of the user password"""
    return sha256(password.encode()).hexdigest()
