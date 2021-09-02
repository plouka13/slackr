import pytest
from error import InputError, AccessError
from auth import auth_login, auth_register
from channels import channels_create, channels_list
from server import reset_req

@pytest.fixture(autouse=True)
def reset_state():
    reset_req()

def test_create_success_public():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    token = user['token']
    channel_id = channels_create(token, 'channel1', True)['channel_id']
    channels = channels_list(token)['channels']
    assert channels[0]['channel_id'] == channel_id

def test_create_success_private():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    token = user['token']
    channel_id = channels_create(token, 'channel1', False)['channel_id']
    channels = channels_list(token)['channels']
    assert channels[0]['channel_id'] == channel_id

def test_create_success_empty_name():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    token = user['token']
    channel_id = channels_create(token, '', True)['channel_id']
    channels = channels_list(token)['channels']
    assert channels[0]['channel_id'] == channel_id
    assert channels[0]['name'] == ''

def test_create_success_same_name():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    token = user['token']
    channels_create(token, 'channel', True)
    channels_create(token, 'channel', True)

    channels = channels_list(token)['channels']
    assert len(channels) == 2
    assert channels[0]['name'] == 'channel'
    assert channels[1]['name'] == 'channel'

def test_create_failure_long_name():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    token = user['token']
    auth_login('bobsmith123@gmail.com', '#abc123')
    with pytest.raises(InputError):
        channels_create(token, 'a' * 21, True)

# Access Error
def test_create_failure_invalid_token():
    auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    with pytest.raises(AccessError):
        channels_create('', 'channel', True)
