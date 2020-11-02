from photo import user_profile_crop_image
from PIL import Image
from test_helpers import register_n_users
from other import clear
import pytest
from error import InputError

IMAGE_1_URL = "https://nas-national-prod.s3.amazonaws.com/styles/hero_cover_bird_page/s3/sfw_fixed_01-29-2011-223.jpg?itok=BIR9fBhk"
def test_crop_simple_crop():
    clear()
    user = register_n_users(1)
    user_profile_crop_image(user["token"], IMAGE_1_URL, 1, 1, 1, 1)

def test_crop_dimensions_not_within_bounds():
    pass

def test_crop_image_not_jpg():
    pass