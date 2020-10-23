import requests
import pytest
from other import clear
from error import AccessError, InputError
from other import admin_userpermission_change
from test_helpers import register_n_users, url, http_register_n_users


def test_admin_userpermission_change_successful():
    clear()
    admin, usera, userb = register_n_users(3, include_admin=True)

    admin_userpermission_change(admin["token"], usera["u_id"], 1)

    # usera should now be able to change other people's permission
    admin_userpermission_change(usera["token"], userb["u_id"], 2)


def test_admin_userpermission_change_fail_self():
    clear()
    usera = register_n_users(1)
    with pytest.raises(AccessError):
        # try to make self admin
        admin_userpermission_change(usera["token"], usera["u_id"], 1)


def test_admin_userpermission_change_fail_other():
    clear()
    admin, usera, userb = register_n_users(3, include_admin=True)

    # cannot change another member's permission
    with pytest.raises(AccessError):
        admin_userpermission_change(usera["token"], userb["u_id"], 1)

    # cannot change admin permission
    with pytest.raises(AccessError):
        admin_userpermission_change(usera["token"], admin["u_id"], 2)


def test_admin_userpermission_change_http(url):
    requests.delete(url + "clear")

    admin, usera, userb = http_register_n_users(url, 3, include_admin=True)

    response = requests.post(
        url + "admin/userpermission/change",
        json={
            "token": admin["token"],
            "u_id": usera["u_id"],
            "permission_id": 1,
        },
    )
    assert response.status_code == 200

    response = requests.post(
        url + "admin/userpermission/change",
        json={
            "token": userb["token"],
            "u_id": usera["u_id"],
            "permission_id": 2,
        },
    )
    assert response.status_code == 403


def test_admin_userpermission_change_invalid_permission_id():
    clear()
    admin, usera = register_n_users(2, include_admin=True)
    with pytest.raises(InputError):
        admin_userpermission_change(admin["token"], usera["u_id"], -1)


def test_admin_userpermission_change_invalid_user_id():
    clear()
    admin = register_n_users(1, include_admin=True)
    with pytest.raises(InputError):
        admin_userpermission_change(admin["token"], -1, 1)
