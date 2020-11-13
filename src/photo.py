from auth import auth_get_current_user_id_from_token
from urllib import request as urllib_request
from PIL import Image
from error import InputError
from database import database
from flask import request
from has_context import get_host_url

# /user/profile/uploadphoto wraps around this function
def user_profile_crop_image(token, img_url, x_start, y_start, x_end, y_end):
    """Given a URL of an image on the internet, crops the image within bounds
    (x_start, y_start) and (x_end, y_end).
    Position (0,0) is the top left."""

    # Ensure token is valid - error checking in function
    user_id = auth_get_current_user_id_from_token(token)

    # Returns (filename, headers) if successful
    try:
        urllib_request.urlretrieve(img_url, "static/" + str(user_id) + ".jpg")
    except:
        raise InputError("img_url returns an HTTP status other than 200")

    original_img = Image.open("static/" + str(user_id) + ".jpg")
    original_width, original_height = original_img.size

    # Ensure image in correct format
    if original_img.format != "JPG" and original_img.format != "JPEG":
        raise InputError("Image uploaded is not a JPG")

    # Basic error checking for given coordinates
    if x_start < 0 or y_start < 0 or x_end < x_start or y_end < y_start:
        raise InputError("given dimensions incorrectly formatted")

    # Error checking that coordinates are within original image
    if x_end > original_width or y_end > original_height:
        raise InputError("Dimensions out of bounds from original image")

    cropped = original_img.crop((x_start, y_start, x_end, y_end))
    cropped.save("static/" + str(user_id) + ".jpg")

    database["users"][user_id]["profile_img_url"] = (
        get_host_url() + "static/" + str(user_id) + ".jpg"
    )
    return {}
