import pytest
from error import InputError, AccessError
import time
from auth import auth_register, auth_logout
from other import standup_active, standup_start
from channels import channels_create
from server import reset_req

LENGTH = 1

@pytest.fixture(autouse=True)
def reset_state():
    reset_req()

def test_standup_active_invalid_token():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']
    auth_logout(user['token'])

    with pytest.raises(AccessError):
        standup_active(user['token'], channel_id)

def test_standup_active_current():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']
    
    standup = standup_start(user['token'], channel_id, LENGTH)
    active = standup_active(user['token'], channel_id)
    
    assert active['is_active'] is True
    assert standup['time_finish'] == active['time_finish']

def test_standup_active_concluded():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']
    
    standup = standup_start(user['token'], channel_id, LENGTH)
    time.sleep(LENGTH)

    active = standup_active(user['token'], channel_id)
    assert active['is_active'] is False
    assert active['time_finish'] is None


def test_standup_active_no_standup():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']

    active = standup_active(user['token'], channel_id)
    assert active['is_active'] is False

def test_standup_active_invalid_channel_id():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']

    with pytest.raises(InputError):
        standup_active(user['token'], 2)

def test_standup_active_not_channel_member():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']
    user2 = auth_register('barbarajones@gmail.com', '#abc123', 'Barbara', 'Jones')

    with pytest.raises(InputError):
        standup_active(user2['token'], channel_id)
