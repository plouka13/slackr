'''
Hangman HTTP Tests
'''
import time
import json
import urllib.request

from channel import channel_details

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
def test_hangman_register(register_two_create_public):
    '''
    Tests /send route
    by sending 1 message
    '''
    fixture = register_two_create_public
    user1 = fixture[0]
    channel_id = fixture[2]

    # first user sends message
    message = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
        'message': "/hangman"
    }).encode('utf-8')
    req1 = urllib.request.Request(f"{BASE_URL}/message/send", data=message, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    json.load(response1)

    # get messages from channel_messages
    messages = get_message(user1['token'], channel_id, 0)

    details = channel_details(user1['token'], channel_id)

    assert len(details['all_members']) == 2
    assert len(details['owner_members']) == 2


def test_hangman_guess(register_two_create_public):
    fixture = register_two_create_public
    user1 = fixture[0]
    user2 = fixture[1]
    channel_id = fixture[2]

    # first user sends message to create hangman
    message = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
        'message': "/hangman"
    }).encode('utf-8')
    req1 = urllib.request.Request(f"{BASE_URL}/message/send", data=message, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    payload1 = json.load(response1)

    guess = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
        'message': "/guess b"
    }).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/send", data=guess, headers=HEADER)
    response2 = urllib.request.urlopen(req2)
    payload2 = json.load(response2)

    messages = get_message(user1['token'], channel_id, 0)['messages']
    hangman = messages[0]
    assert payload1['message_id'] == 1
    assert payload2['message_id'] == 2


