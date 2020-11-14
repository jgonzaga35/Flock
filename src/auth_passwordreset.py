import re
from database import database
from error import InputError, AccessError
import jwt
from hashlib import sha256
import random
import string
from auth import (
    auth_get_user_data_from_id,
    auth_register,
    encrypt,
    is_valid_password,
)
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SENDER_EMAIL = "comp1531mangoteam2@gmail.com"
PASSWORD = "mangosquad123"
PORT = 465

# Generates a random alphanumeric string of specified length.
def generate_reset_code(length):
    letters_and_digits = string.ascii_letters + string.digits
    code = "".join(random.choice(letters_and_digits) for i in range(length))
    return code


# Sends email containing password reset code to receiver_email.
def send_passwordreset_request_email(receiver_email, user, reset_code):

    # Construct message
    message = MIMEMultipart("alternative")
    message["Subject"] = "Password Reset Request"
    message["From"] = SENDER_EMAIL
    message["To"] = receiver_email

    text = """\
    Hello {name},

    Please use the following code to reset your password.
    Code: {reset_code}
    
    Regards, 
    Flockr""".format(
        name=user["first_name"], reset_code=reset_code
    )

    text = MIMEText(text, "plain")
    message.attach(text)

    # Send message
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", PORT, context=context) as server:
        server.login(SENDER_EMAIL, PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, message.as_string())


# Helper to get all user data from their email
def auth_get_user_data_from_email(email):
    for user in database["users"].values():
        if user["email"] == email:
            return user
    raise InputError("Email does not correspond to registered user")


# Sends user an email with a code allowing them to reset their password
def auth_passwordreset_request(email):

    # Check if email is valid and get user data from email
    user = auth_get_user_data_from_email(email)
    length_of_code = 10
    previously_resetted = False

    # Add encrpyted reset_code to database and send email to user
    reset_code = generate_reset_code(length_of_code)
    for user_reset_code in database["reset_codes"].values():
        if user_reset_code["u_id"] == user["id"]:
            user_reset_code["reset_code"] = encrypt(reset_code)
            previously_resetted = True
            break

    # If user has not resetted their password before, add to database.
    # Store reset code in index corresponding to the appropriate user_id
    if not previously_resetted:
        user_reset_code = {
            "u_id": user["id"],
            "reset_code": encrypt(reset_code),
        }
        index = database["reset_codes_head"]
        database["reset_codes"][index] = user_reset_code
        database["reset_codes_head"] += 1

    # Send password reset email to user
    send_passwordreset_request_email(email, user, reset_code)
    return {}


# Helper function to get user id from encrypted reset code
def get_u_id_from_reset_code(reset_code):
    if len(reset_code) == 10:
        reset_code = encrypt(reset_code)

    for user_reset_code in database["reset_codes"].values():
        if reset_code == user_reset_code["reset_code"]:
            return user_reset_code["u_id"]
    raise InputError("Invalid reset code")


# Resets password with a new password given the correct reset code
def auth_passwordreset_reset(reset_code, new_password):
    # Check if new password is valid.
    is_valid_password(new_password)

    # Check if reset_code is valid.
    u_id = get_u_id_from_reset_code(reset_code)

    # Reset password
    database["users"][u_id]["password"] = encrypt(new_password)

    # Delete reset code
    for reset_code_id, code in database["reset_codes"].items():
        if code["reset_code"] == reset_code:
            to_remove = reset_code_id
    del database["reset_codes"][to_remove]

    return {}
