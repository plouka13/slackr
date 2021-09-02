import pytest
from error import InputError, AccessError
from auth import auth_login, auth_register
from channel import channel_join, channel_details, channel_addowner, channel_invite
from channels import channels_create

# pylint: disable=redefined-outer-name
# pylint: disable=missing-docstring

# Successful Tests
def test_addowner_flickr_owner_adds(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']
    details = channel_details(token1, channel_id)

    assert len(details['owner_members']) == 1
    assert len(details['all_members']) == 1


    channel_addowner(token1, channel_id, u_id2)
    details = channel_details(token1, channel_id)
    assert len(details['all_members']) == 2
    assert len(details['owner_members']) == 2


def test_addowner_channel_owner_adds(register_three):
    users = register_three
    __, token1 = users[0]['u_id'], users[0]['token']
    u_id2, token2 = users[1]['u_id'], users[1]['token']
    u_id3, __ = users[2]['u_id'], users[2]['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']
    channel_addowner(token1, channel_id, u_id2)
    channel_addowner(token2, channel_id, u_id3)
    details = channel_details(token1, channel_id)
    assert len(details['owner_members']) == 3
    assert len(details['all_members']) == 3

def test_addowner_multiple_channels_and_users(register_three):
    users = register_three
    __, token1 = users[0]['u_id'], users[0]['token']
    u_id2, token2 = users[1]['u_id'], users[1]['token']
    u_id3, token3 = users[2]['u_id'], users[2]['token']

    channel_id1 = channels_create(token1, 'channel1', True)['channel_id']
    channel_id2 = channels_create(token1, 'channel2', False)['channel_id']
    channel_join(token2, channel_id1)
    channel_join(token3, channel_id1)
    channel_invite(token1, channel_id2, u_id3)
    channel_addowner(token1, channel_id1, u_id2)
    channel_addowner(token1, channel_id2, u_id3)
    details1 = channel_details(token1, channel_id1)
    details2 = channel_details(token1, channel_id2)
    assert len(details1['owner_members']) == 2
    assert len(details1['all_members']) == 3
    assert len(details2['owner_members']) == 2
    assert len(details2['all_members']) == 2



# Input Errors
def test_addowner_invalid_channel(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)  ['channel_id']
    bad_channel_id = -1
    
    with pytest.raises(InputError):
        channel_addowner(token1, bad_channel_id, u_id2)

def test_addowner_failure_no_channel(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']
    
    with pytest.raises(InputError):
        channel_addowner(token1, '', u_id2)

def test_addowner_input_error_nonowner_adds_owner(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']
    channel_join(token2, channel_id)
    
    with pytest.raises(InputError):
        channel_addowner(token2, channel_id, u_id1)

def test_addowner_single_invalid_user(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']
    
    with pytest.raises(InputError):
        channel_addowner(token, channel_id, 100)

def test_addowner_twice_input_error(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']
    channel_addowner(token1, channel_id, u_id2)
    
    with pytest.raises(InputError):
        channel_addowner(token1, channel_id, u_id2)

def test_addowner_to_self(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']
    
    with pytest.raises(InputError):
        channel_addowner(token, channel_id, u_id)

def test_addowner_invalid_user(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']
    bad_u_id2 = -1
    
    with pytest.raises(InputError):
        channel_addowner(token1, channel_id, bad_u_id2)

def test_addowner_failure_no_user(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']
    
    with pytest.raises(InputError):
        channel_addowner(token, channel_id, '')


# Access Errors
def test_addowner_access_error_nonmember_adds_self(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']
    
    with pytest.raises(AccessError):
        channel_addowner(token2, channel_id, u_id2)

def test_addowner_access_error_nonmember_adds_other(register_three):
    users = register_three
    __, token1 = users[0]['u_id'], users[0]['token']
    u_id2, token2 = users[1]['u_id'], users[1]['token']
    u_id3, token3 = users[2]['u_id'], users[2]['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']
    
    with pytest.raises(AccessError):
        channel_addowner(token2, channel_id, u_id3)

def test_addowner_access_error_member_adds_other(register_three):
    users = register_three
    __, token1 = users[0]['u_id'], users[0]['token']
    u_id2, token2 = users[1]['u_id'], users[1]['token']
    u_id3, token3 = users[2]['u_id'], users[2]['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']
    channel_join(token2, channel_id)
    channel_join(token3, channel_id)
    
    with pytest.raises(AccessError):
        channel_addowner(token2, channel_id, u_id3)


def test_addowner_invalid_token(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']
    with pytest.raises(AccessError):
        channel_addowner('', channel_id, u_id2)
