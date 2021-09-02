import pytest
from error import InputError, AccessError
from auth import auth_register
from channels import channels_create
from channel import channel_join, channel_messages
from message import message_send

# pylint: disable=redefined-outer-name
# pylint: disable=missing-docstring

# Success Tests
def test_send_success(register_one):
    u_id, token = register_one
    
    channel_id = channels_create(token, 'channel_name', True)['channel_id']
    
    message_id = message_send(token, channel_id, 'Hello World')['message_id']

    channel_message = channel_messages(token, channel_id, 0)['messages'][0] #gets first dictionary in list of dictionary-messages

    assert channel_message['message_id'] == message_id
    assert channel_message['message'] == 'Hello World'


def test_send_success_empty(register_one):
    u_id, token = register_one
    
    channel_id = channels_create(token, 'channel_name', True)['channel_id']
    
    message_id = message_send(token, channel_id, '')['message_id']

    channel_message = channel_messages(token, channel_id, 0)['messages'][0]

    assert channel_message['message_id'] == message_id
    assert channel_message['message'] == ''

def test_send_success_long(register_one):
    u_id, token = register_one
    
    channel_id = channels_create(token, 'channel_name', True)['channel_id']
    
    message_id = message_send(token, channel_id, 'a' * 1000)['message_id']

    channel_message = channel_messages(token, channel_id, 0)['messages'][0] 

    assert channel_message['message_id'] == message_id
    assert channel_message['message'] == 'a' * 1000

# Failure Tests
# Input Errors
def test_send_failure_long(register_one):
    u_id, token = register_one
    
    channel_id = channels_create(token, 'channel_name', True)['channel_id']
    
    with pytest.raises(InputError) as e:
        message_send(token, channel_id, 'a' * 1001)['message_id']

def test_send_failure_invalid_channel(register_one):
    u_id, token = register_one
    
    channel_id = channels_create(token, 'channel_name', True)['channel_id']
    
    with pytest.raises(InputError):
        message_send(token, 2, 'Hello')


# Access Errors
def test_send_failure_not_in_channel(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']
    
    
    channel_id = channels_create(token1, 'channel_name', True)['channel_id']
    
    with pytest.raises(AccessError):
        message_send(token2, channel_id, 'Hello World')

def test_send_invalid_token(register_one):
    u_id, token = register_one
    
    channel_id = channels_create(token, 'channel_name', True)['channel_id']

    with pytest.raises(AccessError):
        message_send('', channel_id, 'Hello World')





