from channel import channel_messages
from channels import channels_create
from error import InputError, AccessError
import pytest

INVALID_CHANNEL_ID = -1

# Note: Tokens are currently User ID for iteration 1
def test_messages_invalid_channel_ID():
    with pytest.raises(InputError):
        assert channel_messages(0, INVALID_CHANNEL_ID, 0)

def test_messages_negative_start_index():
    new_channel_ID = channels_create(0, 'new_channel', 'is_public')
    with pytest.raises(InputError):
        assert channel_messages(0, new_channel_ID['channel_id'], -1)

def test_messages_invalid_start_index():
    ''' Start is greater than the total # of messages in channel '''
    new_channel_ID = channels_create(0, 'new_channel', 'is_public')
    assert channel_messsages(0, new_channel_ID['channel_id'], 0) == -1
    

def create_test_channel():
    # new_channel_ID = channels_create(0, 'new_channel', 'is_public')