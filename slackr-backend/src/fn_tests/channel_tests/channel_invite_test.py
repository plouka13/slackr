import pytest
from error import InputError, AccessError
from auth import auth_register
from channel import channel_join, channel_details, channel_invite
from channels import channels_create

# pylint: disable=redefined-outer-name
# pylint: disable=missing-docstring

# Successful Tests
def test_invite_success(register_two):
    user1, user2 = register_two
    __, token1 = user1['u_id'], user1['token']
    u_id2, __ = user2['u_id'], user2['token']
    channel_id = channels_create(token1, 'channel1', True)['channel_id']

    channel_invite(token1, channel_id, u_id2)
    details = channel_details(token1, channel_id)
    members = details['all_members']
    assert len(members) == 2

def test_invite_success_already_member(register_two):
    user1, user2 = register_two
    __, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']
    channel_id = channels_create(token1, 'channel1', True)['channel_id']

    channel_join(token2, channel_id)
    channel_invite(token1, channel_id, u_id2)

    details = channel_details(token1, channel_id)
    members = details['all_members']
    assert len(members) == 2

def test_invite_success_self(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']

    channel_invite(token, channel_id, u_id)

    details = channel_details(token, channel_id)
    members = details['all_members']
    assert len(members) == 1

def test_invite_success_private_channel(register_two):
    user1, user2 = register_two
    __, token1 = user1['u_id'], user1['token']
    u_id2, __ = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', False)['channel_id']

    channel_invite(token1, channel_id, u_id2)

    details = channel_details(token1, channel_id)
    members = details['all_members']
    assert len(members) == 2

def test_invite_success_private_channel_nonowner_invites(register_three):
    users = register_three
    __, token1 = users[0]['u_id'], users[0]['token']
    u_id2, token2 = users[1]['u_id'], users[1]['token']
    u_id3, __ = users[2]['u_id'], users[2]['token']

    channel_id = channels_create(token1, 'channel1', False)['channel_id']

    channel_invite(token1, channel_id, u_id2)
    channel_invite(token2, channel_id, u_id3)

    details = channel_details(token1, channel_id)
    members = details['all_members']
    assert len(members) == 3


# Input Errors
def test_invite_invalid_channel(register_two):
    user1, user2 = register_two
    __, token1 = user1['u_id'], user1['token']
    u_id2, __ = user2['u_id'], user2['token']
    channel_id = channels_create(token1, 'channel1', True)['channel_id']

    bad_channel_id = channel_id * 2
    with pytest.raises(InputError):
        channel_invite(token1, bad_channel_id, u_id2)

def test_invite_failure_no_channel(register_two):
    user1, user2 = register_two
    __, token1 = user1['u_id'], user1['token']
    u_id2, __ = user2['u_id'], user2['token']

    channels_create(token1, 'channel1', True)['channel_id']

    with pytest.raises(InputError):
        channel_invite(token1, '', u_id2)

def test_invite_invalid_user(register_two):
    user1, __ = register_two
    __, token1 = user1['u_id'], user1['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']

    bad_u_id2 = ''
    with pytest.raises(InputError):
        channel_invite(token1, channel_id, bad_u_id2)

def test_invite_failure_no_user(register_one):
    __, token1 = register_one

    channel_id = channels_create(token1, 'channel1', True)['channel_id']

    with pytest.raises(InputError):
        channel_invite(token1, channel_id, '')

def test_invite_failure_no_user_or_channel(register_one):
    __, token1 = register_one
    channels_create(token1, 'channel1', True)['channel_id']

    with pytest.raises(InputError):
        channel_invite(token1, '', '')


# Access Errors
def test_invite_user_not_in_channel(register_three):
    users = register_three
    __, token1 = users[0]['u_id'], users[0]['token']
    __, token2 = users[1]['u_id'], users[1]['token']
    u_id3, __ = users[2]['u_id'], users[2]['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']

    with pytest.raises(AccessError):
        channel_invite(token2, channel_id, u_id3)

def test_invite_owner_not_in_channel(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    __, token2 = user2['u_id'], user2['token']
    channel_id = channels_create(token1, 'channel1', True)['channel_id']

    with pytest.raises(AccessError):
        channel_invite(token2, channel_id, u_id1)

def test_invite_invalid_token(register_two):
    user1, user2 = register_two
    __, token1 = user1['u_id'], user1['token']
    u_id2, __ = user2['u_id'], user2['token']
    channel_id = channels_create(token1, 'channel1', True)['channel_id']

    with pytest.raises(AccessError):
        channel_invite('', channel_id, u_id2)
