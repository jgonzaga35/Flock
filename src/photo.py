from auth import auth_get_current_user_id_from_token
import requests
from PIL import Image
from io import BytesIO

# /user/profile/uploadphoto wraps around this function
def user_profile_crop_image(token, img_url, x_start, y_start, x_end, y_end):
    """Given a URL of an image on the internet, crops the image within bounds
    (x_start, y_start) and (x_end, y_end).
    Position (0,0) is the top left."""

    # Ensure token is valid - error checking in function
    user_id = auth_get_current_user_id_from_token(token)

    response = requests.get(img_url)
    if response.status_code != 200:
        raise InputError(f"img_url status code is: {response.status_code()}")

    im = Image.open(BytesIO(response.content))
    # Get dimensions of given image - x_original_start = x_original_end = 0
    x_original_end, y_original_end = im.size()

    # Check given dimensions are within original image
    if (
        x_start < 0 
        or x_start > x_original_end
        or x_end < 0 
        or x_end > x_original_end
        or y_start < 0
        or y_start > y_original_end
        or y_end < 0 
        or y_end > y_original_end
    ):
        raise InputError(
            "any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL"
        )

    # TODO: What to do if start > end or vice versa 

    im.crop((x_start, y_start, x_end, y_end))
    im.show()
    
