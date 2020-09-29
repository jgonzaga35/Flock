from database import database, clear_database
from error import InputError, AccessError
import re

def auth_login(email, password):
    check_email(email)

    for user in database['users']:
        if user['email'] == email:
            if user['password'] == password:
                u_id = user['id']
                token = u_id
                database['active_tokens'].append(token)

                return {
                    'u_id': u_id,
                    'token': token,
                }
            else:
                raise InputError("Wrong password.")
    raise InputError("User doesn't exist.")

def auth_logout(token):
    if token in database['active_tokens']:
        database['active_tokens'].remove(token)
        is_success = True
    else:
        is_success = False

    return {
        'is_success': is_success,
    }

def auth_register(email, password, name_first, name_last):
    input_error_checking(email, password, name_first, name_last)

    for user in database['users']:
        if user['email'] == email:
            raise InputError("Email has been used.")

    u_id = highest_id() + 1
    new_user = {
        'email': email,
        'password': password,
        'first_name': name_first,
        'last_name': name_last,
        'id': u_id
    }
    token = u_id

    database['users'].append(new_user)
    database['active_tokens'].append(token)

    return {
        'u_id': u_id,
        'token': token,
    }


# helper
def auth_get_current_user_id_from_token(token):
    # right now, tokens are just the user ids, so that's just a no-op
    return token

# helper
def auth_get_user_data_from_id(id):
    """ Raises ValueError is the a user with id id doesn't exists """
    for user in database['users']:
        if user['id'] == id:
            return user
    raise ValueError(f"user with id {id} wasn't found in the database")


# Helper function to find the user with the highest id
def highest_id():
    highest = 0
    for user in database['users']:
        if user['id'] > highest:
            highest = user['id']
    return highest

# Helper function for validating an Email
def check_email(email):
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if(re.search(regex,email)):
        return
    else:
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