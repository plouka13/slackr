import pytest
from error import InputError, AccessError
from auth import auth_login, auth_register
from channel import channel_join, channel_leave
from channels import channels_list, channels_create
from server import reset_req

# pylint: disable=redefined-outer-name
# pylint: disable=missing-docstring


# Successful Tests
def test_leave_only_channel(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']
    channel_leave(token, channel_id)

    channels = channels_list(token)['channels']
    assert channels == []

def test_leave_second_channel(register_one):
    __, token = register_one
    channel_id1 = channels_create(token, 'channel1', True)['channel_id']
    channel_id2 = channels_create(token, 'channel2', True)['channel_id']

    channel_leave(token, channel_id1)
    channels = channels_list(token)['channels']
    assert channels[0]['channel_id'] == channel_id2
    assert len(channels) == 1

def test_leave_non_owner(register_two):
    user1, user2 = register_two
    __, token1 = user1['u_id'], user1['token']
    __, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']

    channel_join(token2, channel_id)
    channel_leave(token2, channel_id)

    channels1 = channels_list(token1)['channels']
    assert channels1[0]['channel_id'] == channel_id
    assert len(channels1) == 1

    channels2 = channels_list(token2)['channels']
    assert channels2 == []

def test_leave_owner(register_two):
    user1, user2 = register_two
    __, token1 = user1['u_id'], user1['token']
    __, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']

    channel_join(token2, channel_id)
    channel_leave(token1, channel_id)

    channels1 = channels_list(token1)['channels']
    assert channels1 == []

    channels2 = channels_list(token2)['channels']
    assert channels2[0]['channel_id'] == channel_id
    assert len(channels2) == 1


# Input Errors
def test_leave_invalid_channel(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']
    bad_channel_id = -1
    with pytest.raises(InputError):
        channel_leave(token, bad_channel_id)

def test_leave_failure_no_channel(register_one):
    u_id, token = register_one
    with pytest.raises(InputError):
        channel_leave(token, '')

# Access Errors
def test_leave_empty_member_token(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']

    with pytest.raises(AccessError):
        channel_leave('', channel_id)

def test_leave_invalid_member(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']
    bad_token = token + 'bad'

    with pytest.raises(AccessError):
        channel_leave(bad_token, channel_id)

def test_leave_channel_twice(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']
    channel_leave(token, channel_id)

    with pytest.raises(AccessError):
        channel_leave(token, channel_id)

def test_leave_user_not_in_channel(register_two):
    user1, user2 = register_two
    __, token1 = user1['u_id'], user1['token']
    __, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']

    with pytest.raises(AccessError):
        channel_leave(token2, channel_id)




