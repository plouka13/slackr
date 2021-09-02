import pytest
from error import InputError, AccessError
from auth import auth_login, auth_register
from channel import channel_join, channel_details
from channels import channels_list, channels_create

# pylint: disable=redefined-outer-name
# pylint: disable=missing-docstring


def test_channel_join_success_public_fix(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']

    channel_join(token2, channel_id)
    channels2 = channels_list(token2)['channels']
    assert channels2[0]['channel_id'] == channel_id

    details = channel_details(token1, channel_id)
    members = details['all_members']
    assert len(members) == 2
    assert u_id1 in [members[0]['u_id'], members[1]['u_id']]
    assert u_id2 in [members[0]['u_id'], members[1]['u_id']]

def test_channel_join_success_slackr_owner_private_fix(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']
    channel_id = channels_create(token2, 'channel1', False)['channel_id']

    channel_join(token1, channel_id)
    channels2 = channels_list(token2)['channels']
    assert channels2[0]['channel_id'] == channel_id

    details = channel_details(token1, channel_id)
    members = details['all_members']
    assert len(members) == 2
    assert u_id1 in [members[0]['u_id'], members[1]['u_id']]
    assert u_id2 in [members[0]['u_id'], members[1]['u_id']]


# Input Errors
def test_channel_join_invalid_channel(register_one):
    __, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']
    bad_channel_id = channel_id * 2
    with pytest.raises(InputError):
        channel_join(token, bad_channel_id)

def test_channel_join_failure_no_channel(register_one):
    __, token = register_one
    auth_login('bobsmith123@gmail.com', '#abc123')
    with pytest.raises(InputError):
        channel_join(token, '')

# Access Errors
def test_channel_join_access_error_private(register_two):
    user1, user2 = register_two
    __, token1 = user1['u_id'], user1['token']
    __, token2 = user2['u_id'], user2['token']
    channel_id = channels_create(token1, 'channel1', False)['channel_id']

    with pytest.raises(AccessError):
        channel_join(token2, channel_id)

def test_channel_join_access_error_invalid_token(register_two):
    user1, user2 = register_two
    __, token1 = user1['u_id'], user1['token']
    __, __ = user2['u_id'], user2['token']
    channel_id = channels_create(token1, 'channel1', True)['channel_id']

    with pytest.raises(AccessError):
        channel_join('', channel_id)
