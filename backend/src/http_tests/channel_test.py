import json
import pytest
import urllib.request
import pytest

BASE_URL = 'http://127.0.0.1:8080'
HEADER = {'Content-Type': 'application/json'}


def get_channel_list(token):
    url1 = BASE_URL + "/channels/list?token=" + token
    response1 = urllib.request.urlopen(url1)
    return json.load(response1)

def get_channel_details(user_token, channel_id):
    token = 'token=' + user_token + '&'
    channel = 'channel_id=' + str(channel_id)
    url = BASE_URL + "/channel/details?" + token + channel
    response = urllib.request.urlopen(url)
    return json.load(response)

def get_message(user_token, channel_id, start_num):
    token = 'token=' + user_token + '&'
    channel = 'channel_id=' + str(channel_id) + '&'
    start = 'start=' + str(start_num)
    url = BASE_URL + "/channel/messages?" + token + channel + start
    response = urllib.request.urlopen(url)
    return json.load(response)

def test_channel_join_leave_public(register_two_create_public):
    fixture = register_two_create_public
    user1 = fixture[0]
    user2 = fixture[1]
    channel_id = fixture[2]

    # second user joins public channel
    channel_join = json.dumps({
        'token' : user2['token'],
        'channel_id': channel_id,
    }).encode('utf-8')

    req1 = urllib.request.Request(f"{BASE_URL}/channel/join", data=channel_join, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    json.load(response1)

    # first user (slackr owner) leaves public channel
    channel_leave = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
    }).encode('utf-8')

    req2 = urllib.request.Request(f"{BASE_URL}/channel/leave", data=channel_leave, headers=HEADER)
    response2 = urllib.request.urlopen(req2)
    json.load(response2)

    channel_list1 = get_channel_list(user1['token'])['channels']
    channel_list2 = get_channel_list(user2['token'])['channels']

    assert len(channel_list1) == 0
    assert len(channel_list2) == 1

    details = get_channel_details(user2['token'], channel_id)

    assert len(details['all_members']) == 1
    assert len(details['owner_members']) == 0





def test_channel_invite(register_two_create_public):
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

    channel_list2 = get_channel_list(user2['token'])

    assert len(channel_list2) == 1

    details = get_channel_details(user1['token'], channel_id)

    assert len(details['all_members']) == 2
    assert len(details['owner_members']) == 1


def test_channel_add_remove_owner_details(register_two_create_public):
    fixture = register_two_create_public
    user1 = fixture[0]
    user2 = fixture[1]
    channel_id = fixture[2]

    # first user adds second user as owner
    add_owner = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
        'u_id': user2['u_id']
    }).encode('utf-8')

    req1 = urllib.request.Request(f"{BASE_URL}/channel/addowner", data=add_owner, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    json.load(response1)

    channel_list2 = get_channel_list(user2['token'])

    assert len(channel_list2) == 1

    details = get_channel_details(user1['token'], channel_id)

    assert len(details['all_members']) == 2
    assert len(details['owner_members']) == 2

    # second user removes first user as owner
    remove_owner = json.dumps({
        'token' : user2['token'],
        'channel_id': channel_id,
        'u_id': user1['u_id']
    }).encode('utf-8')

    req2 = urllib.request.Request(f"{BASE_URL}/channel/removeowner", data=remove_owner, headers=HEADER)
    response2 = urllib.request.urlopen(req2)
    json.load(response2)

    channel_list1 = get_channel_list(user1['token'])['channels']

    assert len(channel_list1) == 1
    
    details = get_channel_details(user2['token'], channel_id)
    assert details['name'] == 'channel one'
    assert len(details['all_members']) == 2
    assert len(details['owner_members']) == 1

def test_channel_messages_empty(register_two_create_public):
    fixture = register_two_create_public
    user1 = fixture[0]
    user2 = fixture[1]
    channel_id = fixture[2]

    messages = get_message(user1['token'], channel_id, 0)

    assert len(messages['messages']) == 0
    assert messages['start'] == 0
    assert messages['end'] == -1

def test_channel_messages_one(register_two_create_public):
    fixture = register_two_create_public
    user1 = fixture[0]
    user2 = fixture[1]
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

    messages = get_message(user1['token'], channel_id, 0)
    assert len(messages['messages']) == 1
    assert messages['start'] == 0
    assert messages['end'] == -1


def test_channel_messages_55(register_two_create_public):
    fixture = register_two_create_public
    user1 = fixture[0]
    user2 = fixture[1]
    channel_id = fixture[2]


    for i in range(55):
        # first user sends message
        message = json.dumps({
            'token' : user1['token'],
            'channel_id': channel_id,
            'message': str(i)
        }).encode('utf-8')

        req1 = urllib.request.Request(f"{BASE_URL}/message/send", data=message, headers=HEADER)
        response1 = urllib.request.urlopen(req1)
        json.load(response1)

    # first page
    messages = get_message(user1['token'], channel_id, 0)
    assert len(messages['messages']) == 50
    assert messages['start'] == 0
    assert messages['end'] == 50
    assert messages['messages'][0]['message'] == "54"

    messages = get_message(user1['token'], channel_id, messages['end'])
    assert len(messages['messages']) == 5
    assert messages['start'] == 50
    assert messages['end'] == -1
    assert messages['messages'][4]['message'] == "0"





