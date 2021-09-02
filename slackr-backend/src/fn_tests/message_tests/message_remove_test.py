import pytest
from error import InputError, AccessError
from auth import auth_register
from channels import channels_create
from channel import channel_join, channel_messages
from message import message_send, message_remove

# Success Tests
def test_remove_success(register_one):
    u_id, token = register_one
    
    channel_id = channels_create(token, 'channel_name', True)['channel_id']

    message_id = message_send(token, channel_id, 'Hello World')['message_id']
    message_remove(token, message_id)
    
    messages = channel_messages(token, channel_id, 0)
    assert messages['messages'] == []
    assert messages['end'] == -1

def test_remove_one_of_two(register_one):
    u_id, token = register_one
    
    channel_id = channels_create(token, 'channel_name', True)['channel_id']

    message_id = message_send(token, channel_id, 'Hello World')['message_id']
    message_id2 = message_send(token, channel_id, 'Hi again')['message_id']

    message_remove(token, message_id)
    
    messages = channel_messages(token, channel_id, 0)
    assert messages['messages'][0]['message'] == 'Hi again'
    assert messages['end'] == -1

def test_remove_success_channel_owner(register_three):
    users = register_three
    u_id1, token1 = users[0]['u_id'], users[0]['token']
    u_id2, token2 = users[1]['u_id'], users[1]['token']
    u_id3, token3 = users[2]['u_id'], users[2]['token']
    
    channel_id = channels_create(token2, 'channel1', True)['channel_id']
    channel_join(token3, channel_id)

    message_id = message_send(token3, channel_id, 'Hello World')['message_id']
    
    message_remove(token2, message_id)

    messages = channel_messages(token2, channel_id, 0)
    assert messages['messages'] == []

def test_edit_success_slackr_owner(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']
    
    channel_id = channels_create(token2, 'channel1', True)['channel_id']
    channel_join(token1, channel_id)

    message_id = message_send(token2, channel_id, 'Hello World')['message_id']
    message_id2 = message_send(token2, channel_id, 'Hey again')['message_id']

    message_remove(token1, message_id)
    channel_message = channel_messages(token2, channel_id, 0)['messages'][0] #gets first dictionary in list of dictionary-messages
    
    assert channel_message['message_id'] == message_id2
    assert channel_message['message'] == 'Hey again'

def test_edit_success_non_admin(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel1', True)['channel_id']
    channel_join(token2, channel_id)

    message_id = message_send(token2, channel_id, 'Hello World')['message_id']

    message_remove(token2, message_id)
    
    messages = channel_messages(token2, channel_id, 0)
    assert messages['messages'] == []


def test_remove_success_empty(register_one):
    u_id, token = register_one
    
    channel_id = channels_create(token, 'channel_name', True)['channel_id']

    message_id = message_send(token, channel_id, '')['message_id']
    message_remove(token, message_id)

    messages = channel_messages(token, channel_id, 0)
    assert messages['messages'] == []
    assert messages['end'] == -1

# Error Tests
def test_remove_failure_twice(register_one):
    u_id, token = register_one
    
    channel_id = channels_create(token, 'channel_name', True)['channel_id']
    
    message_id = message_send(token, channel_id, 'Hello World')['message_id']
    message_remove(token, message_id)

    with pytest.raises(InputError):
        message_remove(token, message_id)

def test_remove_failure_not_channel_owner(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']

    channel_id = channels_create(token1, 'channel_name', True)['channel_id']
    channel_join(token2, channel_id)

    message_id = message_send(token1, channel_id, 'Hello World')['message_id']
    
    with pytest.raises(AccessError):
        message_remove(token2, message_id)

def test_remove_failure_not_tokens_message(register_three):
    users = register_three
    u_id1, token1 = users[0]['u_id'], users[0]['token']
    u_id2, token2 = users[1]['u_id'], users[1]['token']
    u_id3, token3 = users[2]['u_id'], users[2]['token']


    channel_id = channels_create(token1, 'channel_name', True)['channel_id']
    channel_join(token2, channel_id)
    channel_join(token3, channel_id)

    message_id = message_send(token2, channel_id, 'Hello World')['message_id']

    with pytest.raises(AccessError):
        message_remove(token3, message_id)

def test_remove_invalid_token(register_one):
    u_id, token = register_one
    
    channel_id = channels_create(token, 'channel_name', True)['channel_id']
    
    message_send(token, channel_id, 'Hello World')
    with pytest.raises(AccessError) as e:
        message_remove('', channel_id)
