from auth import auth_get_current_user_id_from_token
import requests
from PIL import Image

# /user/profile/uploadphoto wraps around this function
def user_profile_crop_image(token, img_url, x_start, y_start, x_end, y_end):
    """Given a URL of an image on the internet, crops the image within bounds
    (x_start, y_start) and (x_end, y_end).
    Position (0,0) is the top left."""

    # Ensure token is valid - error checking in function
    user_id = auth_get_current_user_id_from_token(token)

    # Check given dimensions are within original image
    response = requests.get(image_url)
    if response.status_code() != 200:
        raise InputError(f"img_url status code is: {response.status_code()}")

    im = Image.open(response.content)
    print(im)
    im_dim = im.getbbox()
    print(im_dim)