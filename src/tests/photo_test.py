from photo import user_profile_crop_image
from PIL import Image
from test_helpers import register_n_users
from other import clear
import pytest
from error import InputError, AccessError

IMG_1_URL = "https://diceware.dmuth.org/dice.jpg"
IMG_PNG = "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
BAD_URL = "https://bad.url"

INVALID_USER_ID = -1


def test_crop_dimensions_out_of_bounds():
    clear()
    user = register_n_users(1)
    with pytest.raises(InputError):
        user_profile_crop_image(user["token"], IMG_1_URL, -1, 500, 800, 900)


def test_crop_dimensions_not_within_original():
    clear()
    user = register_n_users(1)
    with pytest.raises(InputError):
        user_profile_crop_image(user["token"], IMG_1_URL, 0, 0, 8000, 9000)


def test_crop_image_not_jpg():
    clear()
    user = register_n_users(1)
    with pytest.raises(InputError):
        user_profile_crop_image(user["token"], IMG_PNG, 40, 50, 80, 90)


def test_bad_url():
    clear()
    user = register_n_users(1)
    with pytest.raises(InputError):
        user_profile_crop_image(user["token"], BAD_URL, 40, 50, 80, 90)


def test_invalid_user():
    clear()
    with pytest.raises(AccessError):
        user_profile_crop_image(INVALID_USER_ID, IMG_1_URL, 40, 50, 80, 90)


def test_simple_crop():
    clear()
    user = register_n_users(1)
    assert user_profile_crop_image(user["token"], IMG_1_URL, 20, 50, 350, 490) == {}
    