import pytest
from error import InputError, AccessError
from auth import auth_login, auth_register
from channel import channel_join, channel_details, channel_addowner, channel_removeowner
from channels import channels_create

# pylint: disable=redefined-outer-name
# pylint: disable=missing-docstring

# Successful Tests
def test_removeowner_owner_removes_channel_creator(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']
    
    channel_id = channels_create(token2, 'channel2', True)['channel_id']
    channel_join(token1, channel_id)

    channel_removeowner(token1, channel_id, u_id2)
    details = channel_details(token1, channel_id)
    assert len(details['owner_members']) == 1
    assert len(details['all_members']) == 2

def test_removeowner_channel_creator_removes_owner(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token2, 'channel2', True)['channel_id']
    channel_join(token1, channel_id)

    channel_removeowner(token2, channel_id, u_id1)
    details = channel_details(token1, channel_id)
    assert len(details['owner_members']) == 1
    assert len(details['all_members']) == 2

def test_removeowner_owner_self(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']
    
    channel_removeowner(token, channel_id, u_id)
    details = channel_details(token, channel_id)
    assert len(details['owner_members']) == 0
    assert len(details['all_members']) == 1

def test_removeowner_self(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']
    channel_id = channels_create(token2, 'channel2', True)['channel_id']
    channel_join(token1, channel_id)

    channel_removeowner(token2, channel_id, u_id2)
    details = channel_details(token1, channel_id)
    assert len(details['owner_members']) == 1
    assert len(details['all_members']) == 2

# Input Errors
def test_removeowner_invalid_channel(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']
    channel_id = channels_create(token1, 'channel1', True)['channel_id']
    channel_addowner(token1, channel_id, u_id2)

    bad_channel_id = -1
    with pytest.raises(InputError):
        channel_removeowner(token1, bad_channel_id, u_id2)

def test_removeowner_failure_no_channel(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']

    channel_addowner(token1, channel_id, u_id2)

    with pytest.raises(InputError):
        channel_removeowner(token1, '', u_id2)

def test_removeowner_invalid_user(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']
    channel_id = channels_create(token1, 'channel1', True)['channel_id']

    bad_u_id2 = -1

    with pytest.raises(InputError):
        channel_removeowner(token1, channel_id, bad_u_id2)

def test_removeowner_failure_no_user(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']

    with pytest.raises(InputError):
        channel_removeowner(token, channel_id, '')


def test_removeowner_non_owner(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']
    channel_join(token2, channel_id)

    with pytest.raises(InputError):
        channel_removeowner(token1, channel_id, u_id2)

def test_removeowner_twice_input_error(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']
    channel_id = channels_create(token1, 'channel1', True)['channel_id']

    channel_addowner(token1, channel_id, u_id2)
    channel_removeowner(token1, channel_id, u_id2)

    with pytest.raises(InputError):
        channel_removeowner(token1, channel_id, u_id2)

def test_removeowner_input_error_nonowner_adds_owner(register_three):
    users = register_three
    __, token1 = users[0]['u_id'], users[0]['token']
    __, token2 = users[1]['u_id'], users[1]['token']
    u_id3, token3 = users[2]['u_id'], users[2]['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']
    channel_join(token2, channel_id)
    channel_join(token3, channel_id)

    with pytest.raises(InputError):
        channel_removeowner(token2, channel_id, u_id3)


# Access Errors
def test_removeowner_access_error_nonowner(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']

    with pytest.raises(AccessError):
        channel_removeowner(token2, channel_id, u_id1)

def test_removeowner_access_error_nonmember_removes_other(register_three):
    users = register_three
    u_id1, token1 = users[0]['u_id'], users[0]['token']
    u_id2, token2 = users[1]['u_id'], users[1]['token']
    u_id3, token3 = users[2]['u_id'], users[2]['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']

    channel_addowner(token1, channel_id, u_id2)
    channel_join(token3, channel_id)

    with pytest.raises(AccessError):
        channel_removeowner(token3, channel_id, u_id2)

def test_removeowner_invalid_token(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']

    with pytest.raises(AccessError):
        channel_removeowner('', channel_id, u_id2)
