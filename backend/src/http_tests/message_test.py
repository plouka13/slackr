'''
Message HTTP Tests
'''
import time
import json
import urllib.request

BASE_URL = 'http://127.0.0.1:8080'
HEADER = {'Content-Type': 'application/json'}

# Helper Function
def get_message(user_token, channel_id, start_num):
    '''
    Returns all messages using
    channel/messages route
    '''
    token = 'token=' + user_token + '&'
    channel = 'channel_id=' + str(channel_id) + '&'
    start = 'start=' + str(start_num)
    url = BASE_URL + "/channel/messages?" + token + channel + start
    response = urllib.request.urlopen(url)
    return json.load(response)

# Test Functions
def test_message_send_one(register_two_create_public):
    '''
    Tests message/send route
    by sending 1 message
    '''
    fixture = register_two_create_public
    user1 = fixture[0]
    channel_id = fixture[2]

    # first user sends message
    message = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
        'message': "hello world"
    }).encode('utf-8')
    req1 = urllib.request.Request(f"{BASE_URL}/message/send", data=message, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    json.load(response1)
    send_time = int(time.time())

    # get messages from channel_messages
    messages = get_message(user1['token'], channel_id, 0)

    test_message = messages['messages'][0]
    assert test_message == {
        'message_id': 1,
        'u_id': 1,
        'message': 'hello world',
        'time_created': send_time,
        'reacts': [],
        'is_pinned': False
    }

def test_message_sendlater(register_two_create_public):
    '''
    Tests message/sendlater route
    by sending 1 message 5 seconds from now
    '''
    fixture = register_two_create_public
    user1 = fixture[0]
    user2 = fixture[1]
    channel_id = fixture[2]

    # inviting second user to public channel
    channel_invite = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
        'u_id': user2['u_id']
    }).encode('utf-8')
    req1 = urllib.request.Request(f"{BASE_URL}/channel/invite", data=channel_invite, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    json.load(response1)
    send_time = int(time.time()) + 5
    # first user sends message
    message = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
        'message': 'hello world',
        'time_sent': send_time
    }).encode('utf-8')
    req1 = urllib.request.Request(f"{BASE_URL}/message/sendlater", data=message, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    json.load(response1)

    # get messages from channel_messages
    messages = get_message(user1['token'], channel_id, 0)
    test_message = messages['messages'][0]
    assert test_message == {
        'message_id': 1,
        'u_id': 1,
        'message': 'hello world',
        'time_created': send_time,
        'reacts': [],
        'is_pinned': False
    }

def test_message_react(register_two_create_public):
    '''
    Tests message/react route
    by sending 1 message and reacting to it
    '''
    fixture = register_two_create_public
    user1 = fixture[0]
    user2 = fixture[1]
    channel_id = fixture[2]

    # inviting second user to public channel
    channel_invite = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
        'u_id': user2['u_id']
    }).encode('utf-8')
    req1 = urllib.request.Request(f"{BASE_URL}/channel/invite", data=channel_invite, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    json.load(response1)

    # first user sends message
    message = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
        'message': "hello world"
    }).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/send", data=message, headers=HEADER)
    response2 = urllib.request.urlopen(req2)
    json.load(response2)
    send_time = int(time.time())


    # get messages from channel_messages
    messages = get_message(user1['token'], channel_id, 0)

    test_message = messages['messages'][0]

    # User2 reacts to user1's message
    react = json.dumps({
        'token': user2['token'],
        'message_id': test_message['message_id'],
        'react_id': 1
    }).encode('utf-8')
    req3 = urllib.request.Request(f"{BASE_URL}/message/react", data=react, headers=HEADER)
    response3 = urllib.request.urlopen(req3)
    json.load(response3)

    # get messages from channel_messages
    messages = get_message(user1['token'], channel_id, 0)

    test_message = messages['messages'][0]

    assert test_message == {
        'message_id': 1,
        'u_id': 1,
        'message': 'hello world',
        'time_created': send_time,
        'reacts': [{
            'react_id': 1,
            'u_ids': [{'u_id': user2['u_id']}],
            'is_this_user_reacted': True
        }],
        'is_pinned': False
    }

def test_message_unreact(register_two_create_public):
    '''
    Tests message/react route
    by sending 1 message, reacting to it
    and then unreacting
    '''
    fixture = register_two_create_public
    user1 = fixture[0]
    user2 = fixture[1]
    channel_id = fixture[2]

    # inviting second user to public channel
    channel_invite = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
        'u_id': user2['u_id']
    }).encode('utf-8')
    req1 = urllib.request.Request(f"{BASE_URL}/channel/invite", data=channel_invite, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    json.load(response1)

    # first user sends message
    message = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
        'message': "hello world"
    }).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/send", data=message, headers=HEADER)
    response2 = urllib.request.urlopen(req2)
    json.load(response2)
    send_time = int(time.time())
    # get messages from channel_messages
    messages = get_message(user1['token'], channel_id, 0)

    test_message = messages['messages'][0]

    # User2 reacts to user1's message
    react = json.dumps({
        'token': user2['token'],
        'message_id': test_message['message_id'],
        'react_id': 1
    }).encode('utf-8')
    req3 = urllib.request.Request(f"{BASE_URL}/message/react", data=react, headers=HEADER)
    response3 = urllib.request.urlopen(req3)
    json.load(response3)

    # get messages from channel_messages
    messages = get_message(user1['token'], channel_id, 0)

    test_message = messages['messages'][0]

    assert test_message == {
        'message_id': 1,
        'u_id': 1,
        'message': 'hello world',
        'time_created': send_time,
        'reacts': [{
            'react_id': 1,
            'u_ids': [{'u_id': user2['u_id']}],
            'is_this_user_reacted': True
        }],
        'is_pinned': False
    }

    unreact = json.dumps({
        'token': user2['token'],
        'message_id': test_message['message_id'],
        'react_id': 1
    }).encode('utf-8')
    req4 = urllib.request.Request(f"{BASE_URL}/message/unreact", data=unreact, headers=HEADER)
    response4 = urllib.request.urlopen(req4)
    json.load(response4)

    # get messages from channel_messages
    messages = get_message(user1['token'], channel_id, 0)

    test_message = messages['messages'][0]

    assert test_message == {
        'message_id': 1,
        'u_id': 1,
        'message': 'hello world',
        'time_created': send_time,
        'reacts': [],
        'is_pinned': False
    }

def test_message_pin(register_two_create_public):
    '''
    Tests message/react route
    by sending 1 message and pinning it
    '''
    fixture = register_two_create_public
    user1 = fixture[0]
    user2 = fixture[1]
    channel_id = fixture[2]

    # inviting second user to public channel
    channel_invite = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
        'u_id': user2['u_id']
    }).encode('utf-8')
    req1 = urllib.request.Request(f"{BASE_URL}/channel/invite", data=channel_invite, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    json.load(response1)

    # first user sends message
    message = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
        'message': "hello world"
    }).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/send", data=message, headers=HEADER)
    response2 = urllib.request.urlopen(req2)
    json.load(response2)
    send_time = int(time.time())

    # get messages from channel_messages
    messages = get_message(user1['token'], channel_id, 0)

    test_message = messages['messages'][0]

    # User2 reacts to user1's message
    pin = json.dumps({
        'token': user1['token'],
        'message_id': test_message['message_id']
    }).encode('utf-8')
    req3 = urllib.request.Request(f"{BASE_URL}/message/pin", data=pin, headers=HEADER)
    response3 = urllib.request.urlopen(req3)
    json.load(response3)

    # get messages from channel_messages
    messages = get_message(user1['token'], channel_id, 0)

    test_message = messages['messages'][0]

    assert test_message == {
        'message_id': 1,
        'u_id': 1,
        'message': 'hello world',
        'time_created': send_time,
        'reacts': [],
        'is_pinned': True
    }

def test_message_unpin(register_two_create_public):
    '''
    Tests message/react route
    by sending 1 message, pinning it and unpinning it
    '''
    fixture = register_two_create_public
    user1 = fixture[0]
    user2 = fixture[1]
    channel_id = fixture[2]

    # inviting second user to public channel
    channel_invite = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
        'u_id': user2['u_id']
    }).encode('utf-8')
    req1 = urllib.request.Request(f"{BASE_URL}/channel/invite", data=channel_invite, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    json.load(response1)

    # first user sends message
    message = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
        'message': "hello world"
    }).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/send", data=message, headers=HEADER)
    response2 = urllib.request.urlopen(req2)
    json.load(response2)
    send_time = int(time.time())

    # get messages from channel_messages
    messages = get_message(user1['token'], channel_id, 0)

    test_message = messages['messages'][0]

    # pin user1's message
    pin = json.dumps({
        'token': user1['token'],
        'message_id': test_message['message_id'],
    }).encode('utf-8')
    req3 = urllib.request.Request(f"{BASE_URL}/message/pin", data=pin, headers=HEADER)
    response3 = urllib.request.urlopen(req3)
    json.load(response3)

    # get messages from channel_messages
    messages = get_message(user1['token'], channel_id, 0)

    test_message = messages['messages'][0]

    assert test_message == {
        'message_id': 1,
        'u_id': 1,
        'message': 'hello world',
        'time_created': send_time,
        'reacts': [],
        'is_pinned': True
    }

    unpin = json.dumps({
        'token': user1['token'],
        'message_id': test_message['message_id']
    }).encode('utf-8')
    req4 = urllib.request.Request(f"{BASE_URL}/message/unpin", data=unpin, headers=HEADER)
    response4 = urllib.request.urlopen(req4)
    json.load(response4)

    # get messages from channel_messages
    messages = get_message(user1['token'], channel_id, 0)

    test_message = messages['messages'][0]

    assert test_message == {
        'message_id': 1,
        'u_id': 1,
        'message': 'hello world',
        'time_created': send_time,
        'reacts': [],
        'is_pinned': False
    }

def test_message_remove(register_two_create_public):
    '''
    Tests message/remove route
    by sending 1 message and removing it
    '''
    fixture = register_two_create_public
    user1 = fixture[0]
    user2 = fixture[1]
    channel_id = fixture[2]

    # inviting second user to public channel
    channel_invite = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
        'u_id': user2['u_id']
    }).encode('utf-8')
    req1 = urllib.request.Request(f"{BASE_URL}/channel/invite", data=channel_invite, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    json.load(response1)

    # first user sends message
    message = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
        'message': "hello world"
    }).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/send", data=message, headers=HEADER)
    response2 = urllib.request.urlopen(req2)
    json.load(response2)
    send_time = int(time.time())

    # get messages from channel_messages
    messages = get_message(user1['token'], channel_id, 0)

    test_message = messages['messages'][0]

    assert test_message == {
        'message_id': 1,
        'u_id': 1,
        'message': 'hello world',
        'time_created': send_time,
        'reacts': [],
        'is_pinned': False
    }

    # Remove Message
    remove = json.dumps({
        'token': user1['token'],
        'message_id': test_message['message_id']
    }).encode('utf-8')
    remove_url = f"{BASE_URL}/message/remove"
    req3 = urllib.request.Request(f"{remove_url}", data=remove, headers=HEADER, method='DELETE')
    response3 = urllib.request.urlopen(req3)
    json.load(response3)

    # get messages from channel_messages
    messages = get_message(user1['token'], channel_id, 0)

    assert len(messages['messages']) == 0

def test_message_edit(register_two_create_public):
    '''
    Tests message/edit route
    by sending 1 message and editting its contents
    '''
    fixture = register_two_create_public
    user1 = fixture[0]
    user2 = fixture[1]
    channel_id = fixture[2]

    # inviting second user to public channel
    channel_invite = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
        'u_id': user2['u_id']
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/invite", data=channel_invite, headers=HEADER)
    response = urllib.request.urlopen(req)
    json.load(response)

    # first user sends message
    message = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
        'message': "hello world"
    }).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/send", data=message, headers=HEADER)
    response2 = urllib.request.urlopen(req2)
    json.load(response2)
    send_time = int(time.time())

    # get messages from channel_messages
    messages = get_message(user1['token'], channel_id, 0)

    test_message = messages['messages'][0]
    assert test_message == {
        'message_id': 1,
        'u_id': 1,
        'message': 'hello world',
        'time_created': send_time,
        'reacts': [],
        'is_pinned': False
    }

    # Edit Message
    edit = json.dumps({
        'token': user1['token'],
        'message_id': test_message['message_id'],
        'message': 'Hey Mars!'
    }).encode('utf-8')
    edit_url = f"{BASE_URL}/message/edit"
    req3 = urllib.request.Request(f"{edit_url}", data=edit, headers=HEADER, method='PUT')
    response3 = urllib.request.urlopen(req3)
    json.load(response3)

    # get messages from channel_messages
    messages = get_message(user1['token'], channel_id, 0)

    test_message = messages['messages'][0]

    assert test_message == {
        'message_id': 1,
        'u_id': 1,
        'message': 'Hey Mars!',
        'time_created': send_time,
        'reacts': [],
        'is_pinned': False
    }
