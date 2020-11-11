from auth import auth_get_current_user_id_from_token
from urllib import request
from PIL import Image
from error import InputError

IMG = "https://images.squarespace-cdn.com/content/v1/588a02f11b10e3d4643f5c35/1529414023053-VYOZFJHYGK4ZP4J7ROU1/ke17ZwdGBToddI8pDm48kOAAkRx_t64z7DtxIgl8aowUqsxRUqqbr1mOJYKfIPR7LoDQ9mXPOjoJoqy81S2I8N_N4V1vUb5AoIIIbLZhVYxCRW4BPu10St3TBAUQYVKcnu583A7KLrl1h8MSxVTZxTM6WgCx0nvYGVcb13pyTIh-GFpiPL4F-R40gAFIkKTs/agile-graphic.jpg"

# /user/profile/uploadphoto wraps around this function
def user_profile_crop_image(token, img_url, x_start, y_start, x_end, y_end):
    """Given a URL of an image on the internet, crops the image within bounds
    (x_start, y_start) and (x_end, y_end).
    Position (0,0) is the top left."""

    # Ensure token is valid - error checking in function
    # user_id = auth_get_current_user_id_from_token(token)

    # Returns (filename, headers) if successful
    try:
        response = request.urlretrieve(img_url, "user_photos/" + str(user_id))
    except:
        raise InputError("img_url returns an HTTP status other than 200")

    original_img = Image.open("user_photos/" + str(user_id))
    original_width, original_height = original_img.size

    # Ensure image in correct format
    if(original_img.format != "JPG" and original_img.format != "JPEG"):
        raise InputError("Image uploaded is not a JPG")

    # Basic error checking for given coordinates
    if x_start < 0 or y_start < 0 or x_end < x_start or y_end < y_start:
        raise InputError("given dimensions incorrectly formatted")

    # Error checking that coordinates are within original image
    if x_end > original_width or y_end > original_height:
        raise InputError("Dimensions out of bounds from original image")

    cropped = original_img.crop((x_start, y_start, x_end, y_end))
    cropped.save("user_photos/" + str(user_id))