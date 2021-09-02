import pytest
from error import InputError, AccessError
from auth import auth_login, auth_register
from channel import channel_join, channel_details, channel_leave, channel_addowner, channel_removeowner
from channels import channels_create

# pylint: disable=redefined-outer-name
# pylint: disable=missing-docstring


# Successful Tests
def test_details_one_member(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']

    details = channel_details(token, channel_id)
    assert details['name'] == 'channel1'
    assert details['owner_members'][0]['u_id'] == u_id

    members = details['all_members']
    assert len(members) == 1
    assert members[0]['u_id'] == u_id

def test_details_two_members(register_two):
    user1, user2 = register_two
    __, token1 = user1['u_id'], user1['token']
    __, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']
    channel_join(token2, channel_id)

    details = channel_details(token1, channel_id)
    members = details['all_members']
    assert details['name'] == 'channel1'
    assert len(details['owner_members']) == 1
    assert len(members) == 2

def test_details_two_channels(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']
    channel_id2 = channels_create(token2, 'channel2', True)['channel_id']
    channel_join(token2, channel_id)

    details = channel_details(token1, channel_id)
    assert details['name'] == 'channel1'
    assert len(details['owner_members']) == 1
    assert len(details['all_members']) == 2

    details2 = channel_details(token2, channel_id2)
    assert details2['name'] == 'channel2'
    assert len(details2['owner_members']) == 1
    assert len(details2['all_members']) == 1
 
# Updating owner tests
# Assumes addowner works
def test_details_add_owner(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']
    channel_join(token2, channel_id)
    channel_addowner(token1, channel_id, u_id2)
    details = channel_details(token1, channel_id)
    
    assert len(details['owner_members']) == 2
    assert details['owner_members'][0]['u_id'] in [u_id1, u_id2]
    assert details['owner_members'][1]['u_id'] in [u_id1, u_id2]
    assert len(details['all_members']) == 2

def test_details_add_and_remove_owners(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']
    channel_join(token2, channel_id)
    channel_addowner(token1, channel_id, u_id2)
    channel_removeowner(token1, channel_id, u_id2)
    details = channel_details(token1, channel_id)
    
    assert len(details['owner_members']) == 1
    assert details['owner_members'][0]['u_id'] == u_id1
    assert len(details['all_members']) == 2

# Input Errors
def test_details_invalid_channel(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']
    bad_channel_id = -1

    with pytest.raises(InputError):
        channel_details(token, bad_channel_id)

def test_details_failure_no_channel(register_one):
    u_id, token = register_one  
    with pytest.raises(InputError):
        channel_details(token, '')


# Access Errors
def test_details_empty_member_token(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']

    with pytest.raises(AccessError):
        channel_details('', channel_id)

def test_details_invalid_member(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']
    bad_token = token + 'bad'

    with pytest.raises(AccessError):
        channel_details(bad_token, channel_id)

def test_details_user_not_in_channel(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']

    with pytest.raises(AccessError):
        channel_details(token2, channel_id)

def test_details_user_left_channel(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']

    channel_join(token2, channel_id)
    channel_leave(token2, channel_id)

    with pytest.raises(AccessError):
        channel_details(token2, channel_id)

def test_details_only_member_leaves(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']
    channel_leave(token, channel_id)

    with pytest.raises(AccessError):
        channel_details(token, channel_id)

def test_details_invalid_token(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']

    with pytest.raises(AccessError):
        channel_details('', channel_id)

