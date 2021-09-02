import pytest
from error import InputError, AccessError
from auth import auth_register
from channel import channel_messages, channel_join
from channels import channels_create
from message import message_send

# pylint: disable=redefined-outer-name
# pylint: disable=missing-docstring

# Success Tests
def test_messages_success_one_message(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']

    message_id = message_send(token, channel_id, 'Hello World')['message_id']
    channel_msg = channel_messages(token, channel_id, 0)

    assert channel_msg['messages'][0]['message_id'] == message_id
    assert  channel_msg['start'] == 0
    assert channel_msg['end'] == -1


def test_messages_success_channel_owner(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']
    channel_id = channels_create(token2, 'channel1', True)['channel_id']

    channel_join(token1, channel_id)
    message_send(token1, channel_id, 'Hello World')['message_id']

    messages = channel_messages(token2, channel_id, 0)['messages']

    assert len(messages) == 1

def test_messages_success_channel_member(register_three):
    users = register_three
    u_id1, token1 = users[0]['u_id'], users[0]['token']
    u_id2, token2 = users[1]['u_id'], users[1]['token']
    u_id3, token3 = users[2]['u_id'], users[2]['token']

    channel_id = channels_create(token2, 'channel1', True)['channel_id']

    channel_join(token1, channel_id)
    channel_join(token3, channel_id)
    message_send(token1, channel_id, 'Hello World')

    messages = channel_messages(token3, channel_id, 0)['messages']

    assert len(messages) == 1

def test_messages_success_multiple_messages(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']

    message_id1 = message_send(token, channel_id, 'Hello World')['message_id']
    message_id2 = message_send(token, channel_id, 'Hello World')['message_id']
    message_id3 = message_send(token, channel_id, 'Hello World')['message_id']
    message_id4 = message_send(token, channel_id, 'Hello World')['message_id']
    message_id5 = message_send(token, channel_id, 'Hello World')['message_id']
    
    messages = channel_messages(token, channel_id, 0)['messages']
    assert len(messages) == 5

def test_messages_success_chronological_order(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']

    message_id1 = message_send(token, channel_id, 'One')['message_id']
    message_id2 = message_send(token, channel_id, 'Two')['message_id']
    message_id3 = message_send(token, channel_id, 'Three')['message_id']
    
    messages = channel_messages(token, channel_id, 0)['messages']
    assert len(messages) == 3
    assert messages[0]['message_id'] == message_id3
    assert messages[1]['message_id'] == message_id2
    assert messages[2]['message_id'] == message_id1

    assert messages[0]['message'] == 'Three'
    assert messages[1]['message'] == 'Two'
    assert messages[2]['message'] == 'One'

def test_messages_success_chronological_order_two_pages(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']

    for i in range(55):
        message_send(token, channel_id, str(i))

    messages = channel_messages(token, channel_id, 0)['messages']
    assert len(messages) == 50
    assert messages[0]['message'] == "54"
    assert messages[49]['message'] == "5"

    messages2 = channel_messages(token, channel_id, 50)['messages']
    assert len(messages2) == 5
    assert messages2[0]['message'] == "4"
    assert messages2[4]['message'] == '0'


def test_messages_success_55_first_page(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']
    
    for i in range(55):
        message_send(token, channel_id, 'Hello World')
    
    channel_msg = channel_messages(token, channel_id, 0)

    assert len(channel_msg['messages']) == 50
    assert channel_msg['start'] == 0
    assert channel_msg['end'] == 50

def test_messages_success_55_second_page(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']
    
    for i in range(55):
        message_send(token, channel_id, 'Hello World')
    
    channel_msg = channel_messages(token, channel_id, 0)
    end = channel_msg['end']
    assert channel_msg['start'] == 0
    assert channel_msg['end'] == 50

    channel_msg2 = channel_messages(token, channel_id, end)

    assert len(channel_msg2['messages']) == 5
    assert channel_msg2['start'] == 50
    assert channel_msg2['end'] == -1

def test_messages_success_124_messages_last_page(register_one):
    u_id, token = register_one
    channel_id = channels_create(token, 'channel1', True)['channel_id']

    message_list = []
    for i in range(124):
        message_send(token, channel_id, 'Hello World')
    
    channel_msg = channel_messages(token, channel_id, 100)

    assert len(channel_msg['messages']) == 24
    assert channel_msg['start'] == 100
    assert channel_msg['end'] == -1


# Error Tests
# Input Errors
def test_messages_failure_invalid_channel(register_one):
    u_id, token = register_one

    channel_id = channels_create(token, 'channel1', True)['channel_id']
    bad_channel_id = -1
    with pytest.raises(InputError):
        channel_messages(token, bad_channel_id, 0)

def test_messages_failure_start_more_than_messages(register_one):
    u_id, token = register_one

    channel_id = channels_create(token, 'channel1', True)['channel_id']

    message_id1 = message_send(token, channel_id, 'Hello World')['message_id']
    message_id2 = message_send(token, channel_id, 'Hi there!')['message_id']
    with pytest.raises(InputError):
        channel_messages(token, channel_id, 3)

def test_messages_failure_start_more_than_no_messages(register_one):
    u_id, token = register_one

    channel_id = channels_create(token, 'channel1', True)['channel_id']

    with pytest.raises(InputError):
        channel_messages(token, channel_id, 1)

def test_messages_failure_not_in_channel(register_two):
    user1, user2 = register_two
    u_id1, token1 = user1['u_id'], user1['token']
    u_id2, token2 = user2['u_id'], user2['token']
    
    channel_id = channels_create(token1, 'channel1', True)['channel_id']
    message_id = message_send(token1, channel_id, 'Hello World')['message_id']
    with pytest.raises(AccessError):
        channel_messages(token2, channel_id, 0)

def test_messages_invalid_token(register_one):
    u_id, token = register_one
    
    channel_id = channels_create(token, 'channel1', True)['channel_id']
    
    message_send(token, channel_id, 'Hello World')['message_id']
    with pytest.raises(AccessError):
        channel_messages('', u_id, 0)
