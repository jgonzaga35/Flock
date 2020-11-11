import requests
from test_helpers import url, http_register_n_users

IMG_1_URL = "https://diceware.dmuth.org/dice.jpg"
IMG_PNG = "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
BAD_URL = "https://bad.url"

def test_simple(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    response = requests.post(
        url + "user/profile/uploadphoto",
        json={
            "token": user["token"],
            "img_url": IMG_1_URL,
            "x_start": 0,
            "y_start": 0,
            "x_end": 300,
            "y_end": 300,
        }
    )

    assert response.status_code == 200

    response = requests.get(
        url + "user/profile",
        params={
            "token": user["token"],
            "u_id": user["u_id"],
        },
    )
    assert response.status_code == 200

    user_data = response.json()
    url = user_data["user"]["profile_img_url"]
    assert url.startswith("http://")
    assert url.endswith("/static/" + str(user["u_id"]) + ".jpg")
   