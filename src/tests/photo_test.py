from photo import user_profile_crop_image
from PIL import Image
from test_helpers import register_n_users
from other import clear
import pytest
from error import InputError

IMG_1_URL = "https://images.squarespace-cdn.com/content/v1/588a02f11b10e3d4643f5c35/1529414023053-VYOZFJHYGK4ZP4J7ROU1/ke17ZwdGBToddI8pDm48kOAAkRx_t64z7DtxIgl8aowUqsxRUqqbr1mOJYKfIPR7LoDQ9mXPOjoJoqy81S2I8N_N4V1vUb5AoIIIbLZhVYxCRW4BPu10St3TBAUQYVKcnu583A7KLrl1h8MSxVTZxTM6WgCx0nvYGVcb13pyTIh-GFpiPL4F-R40gAFIkKTs/agile-graphic.jpg"
IMG_PNG = "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
BAD_URL = "https://bad.url"

INVALID_USER_ID = -1

def test_crop_dimensions_out_of_bounds():
    clear()
    user = register_n_users(1)
    with pytest.raises(InputError):
        user_profile_crop_image(user["token"], IMG_1_URL, -1, 500, 800, 900)

def test_crop_image_not_jpg():
    clear()
    user = register_n_users(1)
    with pytest.raises(InputError):
        user_profile_crop_image(user["token"], IMG_1_URL, 40, 50, 80, 90)

def test_bad_url():
    clear()
    user = register_n_users(1)
    with pytest.raises(InputError):
        user_profile_crop_image(user["token"], BAD_URL, 40, 50, 80, 90)

def test_invalid_user():
    clear()
    with pytest.raises(InputError):
        user_profile_crop_image(INVALID_USER_ID, IMG_1_URL, -1, 500, 800, 900)