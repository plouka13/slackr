import pytest
from error import InputError, AccessError
from auth import auth_register, auth_logout
from other import search
from channels import channels_create
from channel import channel_join, channel_messages, channel_leave
from message import message_send, message_edit, message_remove
from server import reset_req

@pytest.fixture(autouse=True)
def reset_state():
    reset_req()

def test_search_invalid_token():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    auth_logout(user['token'])
    
    with pytest.raises(AccessError):
        search(user['token'], 'Hello World')

def test_search_no_messages():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    
    found_messages = search(user['token'], 'Hello World')
    assert len(found_messages['messages']) == 0   

def test_search_exact_match():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    
    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']
    message_id = message_send(user['token'], channel_id, 'Hello World')
    
    found_messages = search(user['token'], 'Hello World')
    assert len(found_messages['messages']) == 1

def test_search_similar_match1():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    
    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']
    message_id = message_send(user['token'], channel_id, 'Hello World!')
    
    found_messages = search(user['token'], 'Hello World')
    assert len(found_messages['messages']) == 1

def test_search_similar_match2():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']
    message_id = message_send(user['token'], channel_id, 'iHelloi')
    found_messages = search(user['token'], 'Hello')
    assert len(found_messages['messages']) == 1

def test_search_not_case_sensitive():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    
    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']
    message_id = message_send(user['token'], channel_id, 'hello')
    
    found_messages = search(user['token'], 'HELLO')
    assert len(found_messages['messages']) == 1
    
def test_search_multiple_occurances():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    
    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']
    message_send(user['token'], channel_id, 'Hello World')
    message_send(user['token'], channel_id, 'Hello World')
    message_send(user['token'], channel_id, 'Hello World')
    
    found_messages = search(user['token'], 'Hello World')
    assert len(found_messages['messages']) == 3

def test_search_multiple_senders():
    user1 = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_register('barbarajones@gmail.com', '#abc123', 'Barbara', 'Jones')
    
    channel_id = channels_create(user1['token'], 'channel1', True)['channel_id']
    channel_join(user2['token'], channel_id)
    
    message_id1 = message_send(user1['token'], channel_id, 'Hello World')
    message_id2 = message_send(user2['token'], channel_id, 'Hello World!')
    found_messages = search(user1['token'], 'Hello World')
    assert len(found_messages['messages']) == 2

def test_search_newest_msg_first():
    user1 = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    
    channel_id = channels_create(user1['token'], 'channel1', True)['channel_id']
    
    message_send(user1['token'], channel_id, 'Hello World 1')
    message_send(user1['token'], channel_id, 'Hello World 2')

    found_messages = search(user1['token'], 'Hello world')
    assert found_messages['messages'][0]['message'] == 'Hello World 2'
    assert found_messages['messages'][1]['message'] == 'Hello World 1'

def test_search_newest_msg_first_different_channels():
    user1 = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    
    channel_id1 = channels_create(user1['token'], 'channel1', True)['channel_id']
    channel_id2 = channels_create(user1['token'], 'channel2', True)['channel_id']
    
    message_send(user1['token'], channel_id1, 'Hello World 1')
    message_send(user1['token'], channel_id2, 'Hello World 3')
    
    message_send(user1['token'], channel_id1, 'Hello World 2')
    message_send(user1['token'], channel_id2, 'Hello World 4')

    found_messages = search(user1['token'], 'Hello world')
    assert found_messages['messages'][0]['message'] == 'Hello World 2'
    assert found_messages['messages'][1]['message'] == 'Hello World 1' 
    assert found_messages['messages'][2]['message'] == 'Hello World 4'
    assert found_messages['messages'][3]['message'] == 'Hello World 3'  
  
def test_search_multiple_senders_newest_msg_first():
    user1 = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_register('barbarajones@gmail.com', '#abc123', 'Barbara', 'Jones')
    
    channel_id = channels_create(user1['token'], 'channel1', True)['channel_id']
    channel_join(user2['token'], channel_id)
    
    message_send(user1['token'], channel_id, 'Hello World 1')
    message_send(user2['token'], channel_id, 'Hello World 2')
    message_send(user2['token'], channel_id, 'Hello World 3')
    message_send(user2['token'], channel_id, 'Hello World 4')
    message_send(user1['token'], channel_id, 'Hello World 5')

    found_messages = search(user1['token'], 'Hello world')
    assert found_messages['messages'][0]['message'] == 'Hello World 5'
    assert found_messages['messages'][1]['message'] == 'Hello World 4'
    assert found_messages['messages'][2]['message'] == 'Hello World 3'
    assert found_messages['messages'][3]['message'] == 'Hello World 2'
    assert found_messages['messages'][4]['message'] == 'Hello World 1'

def test_search_multiple_public_channels():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    
    channel_id1 = channels_create(user['token'], 'channel1', True)['channel_id']
    message_id1 = message_send(user['token'], channel_id1, 'Hello World')
    
    channel_id2 = channels_create(user['token'], 'channel2', True)['channel_id']
    message_id2 = message_send(user['token'], channel_id2, 'Hello World!')
    
    channel_id3 = channels_create(user['token'], 'channel3', True)['channel_id']
    message_id3 = message_send(user['token'], channel_id3, 'Hello World :)')
    
    found_messages = search(user['token'], 'Hello World')
    assert len(found_messages['messages']) == 3

def test_search_joined_public_channel():
    user1 = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_register('barbarajones@gmail.com', '#abc123', 'Barbara', 'Jones')
    
    channel_id = channels_create(user1['token'], 'channel1', True)['channel_id']
    message_id = message_send(user1['token'], channel_id, 'Hello World :)')
    
    channel_join(user2['token'], channel_id)
    
    found_messages = search(user2['token'], 'Hello World')
    assert len(found_messages['messages']) == 1

def test_search_private_channel_no_access():
    user1 = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_register('barbarajones@gmail.com', '#abc123', 'Barbara', 'Jones')
    
    channel_id = channels_create(user1['token'], 'channel1', False)['channel_id']
    message_id = message_send(user1['token'], channel_id, 'Hello World :)')
    
    found_messages = search(user2['token'], 'Hello World')
    assert len(found_messages['messages']) == 0

def test_search_left_channel():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    
    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']
    message_id = message_send(user['token'], channel_id, 'Hello World :)')
    
    channel_leave(user['token'], channel_id)
    
    found_messages = search(user['token'], 'Hello World')
    assert len(found_messages['messages']) == 0

def test_search_removed_message():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    
    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']
    message_id = message_send(user['token'], channel_id, 'Hello World')['message_id']
    message_remove(user['token'], message_id)
    
    found_messages = search(user['token'], 'Hello World')
    assert len(found_messages['messages']) == 0

def test_search_editted_message_original():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    
    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']
    message_id = message_send(user['token'], channel_id, 'Hello World')['message_id']
    message_edit(user['token'], message_id, 'Hi Mars')
    
    found_messages = search(user['token'], 'Hello World')
    assert len(found_messages['messages']) == 0

def test_search_editted_message_new():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    
    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']
    message_id = message_send(user['token'], channel_id, 'Hello World')['message_id']
    message_edit(user['token'], message_id, 'Hi Mars')
    
    found_messages = search(user['token'], 'Hi Mars')
    assert len(found_messages['messages']) == 1
