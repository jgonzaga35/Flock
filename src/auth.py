import re

def auth_login(email, password):
    check_email(email)

    return {
        'u_id': 1,
        'token': '12345',
    }

def auth_logout(token):
    return {
        'is_success': True,
    }

def auth_register(email, password, name_first, name_last):
    check_email(email)

    return {
        'u_id': 1,
        'token': '12345',
    }

# Helper function for validating an Email 
def check_email(email):  
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if(re.search(regex,email)):  
        return
    else:  
        raise InputError("Email inputted is invalid.")