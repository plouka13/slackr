import pytest
from error import AccessError
from auth import auth_register
from channels import channels_create, channels_list
from channel import channel_join
from server import reset_req

@pytest.fixture(autouse=True)
def reset_state():
    reset_req()

def test_list_no_channel():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    token = user['token']
    channels = channels_list(token)['channels']
    assert channels == []

def test_list_one_user():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    token = user['token']
    channel_id = channels_create(token, 'channel1', True)['channel_id']
    channels = channels_list(token)['channels']
    assert len(channels) == 1
    assert channels[0]['channel_id'] == channel_id

def test_list_two_same_user():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    token = user['token']
    channel_id1 = channels_create(token, 'channel1', True)['channel_id']
    channel_id2 = channels_create(token, 'channel2', False)['channel_id']

    channels = channels_list(token)['channels']
    assert len(channels) == 2
    assert channels[0]['channel_id'] in [channel_id1, channel_id2]
    assert channels[1]['channel_id'] in [channel_id1, channel_id2]

def test_list_two_users_and_channels():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    token = user['token']
    user2 = auth_register('brucejones@aol.com', 'xyz789!', 'Bruce', 'Jones')
    token2 = user2['token']

    channel_id1 = channels_create(token, 'channel1', True)['channel_id']
    channel_id2 = channels_create(token2, 'channel2', False)['channel_id']
    channels1 = channels_list(token)['channels']
    channels2 = channels_list(token2)['channels']

    assert channels1[0]['channel_id'] == channel_id1
    assert channels2[0]['channel_id'] == channel_id2

    assert len(channels1) == 1
    assert len(channels2) == 1

def test_list_two_users_same_channel():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    token = user['token']
    user2 = auth_register('brucejones@aol.com', 'xyz789!', 'Bruce', 'Jones')
    token2 = user2['token']

    channel_id = channels_create(token, 'channel1', True)['channel_id']
    channel_join(token2, channel_id)
    channels1 = channels_list(token)['channels']
    channels2 = channels_list(token2)['channels']

    assert channels1[0]['channel_id'] == channel_id
    assert channels2[0]['channel_id'] == channel_id

# Access Error
def test_list_failure_invalid_token():
    auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    with pytest.raises(AccessError):
        channels_list('')
