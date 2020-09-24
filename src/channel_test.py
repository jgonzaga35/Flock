from channel import channel_details, channel_leave, channel_join, channel_addowner
from channels import channels_create
from auth import auth_login, auth_register
import pytest


@pytest.fixture
def initialize_user():
    #user's information includes a dictionary {token, u_id}
    user_information = auth_register('baixu.must@gmail.com', 'qweAsd1232566', 'White', 'Black')
    auth_login('baixu.must@gmail.com', 'qweAsd1232566')
    return user_information
    
def test_channel_join_success(initialize_user):
    u_id, token = initialize_user['u_id'], initialize_user['token']
    channel_id = channels_create(token, "Channel_A", True)
    channel_join(token, channel_id)

def test_channel_join_invalid_channelId():
    pass
def test_channel_join_user_not_auth():
    pass
def test_channel_leave_success():
    pass
def test_channel_leave_user_not_exist():
    pass
def test_channel_leave_channel_id_invalid():
    pass