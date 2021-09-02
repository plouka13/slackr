import pytest
from error import InputError, AccessError
import time
from auth import auth_register, auth_logout
from other import standup_start
from channels import channels_create
from server import reset_req

LENGTH = 1

@pytest.fixture(autouse=True)
def reset_state():
    reset_req()

def test_standup_start_invalid_token():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']
    auth_logout(user['token'])

    with pytest.raises(AccessError):
        standup_start(user['token'], channel_id, LENGTH)

def test_standup_start_success():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']
    standup = standup_start(user['token'], channel_id, LENGTH)
    finish_time = int(time.time()) + LENGTH
    
    assert standup['time_finish'] == finish_time

def test_standup_start_invalid_channel_id():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_register('barbarajones@gmail.com', '#abc123', 'Barbara', 'Jones')

    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']

    with pytest.raises(InputError):
        standup_start(user2['token'], channel_id, LENGTH)

def test_standup_start_invalid_length():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_register('barbarajones@gmail.com', '#abc123', 'Barbara', 'Jones')

    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']

    with pytest.raises(InputError):
        standup_start(user2['token'], channel_id, 0)

def test_standup_start_not_channel_member():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']

    with pytest.raises(InputError):
        standup_start(user['token'], 2, LENGTH)

def test_standup_start_standup_already_commenced():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']
    standup_start(user['token'], channel_id, LENGTH)
    
    with pytest.raises(InputError):
        standup_start(user['token'], channel_id, LENGTH)
