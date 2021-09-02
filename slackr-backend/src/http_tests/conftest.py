import pytest
from auth import auth_register
from server import reset_req
import json
import urllib.request

BASE_URL = 'http://127.0.0.1:8080'
HEADER = {'Content-Type': 'application/json'}

@pytest.fixture (autouse=True)
def reset_state():
    req1 = urllib.request.Request(f"{BASE_URL}/workspace/reset", data=None, headers=HEADER, method='POST')
    response1 = urllib.request.urlopen(req1)
    json.load(response1)
    #reset_req()

@pytest.fixture
def register_one():
    user1 = json.dumps({
        'email' : 'michaelscott@gmail.com',
        'password': 'dundermifflen1',
        'name_first': 'Michael',
        'name_last': 'Scott'
    }).encode('utf-8')

    req1 = urllib.request.Request(f"{BASE_URL}/auth/register", data=user1, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    payload1 = json.load(response1)
    return payload1

@pytest.fixture
def register_two():
    user1 = json.dumps({
        'email' : 'michaelscott@gmail.com',
        'password': 'dundermifflen1',
        'name_first': 'Michael',
        'name_last': 'Scott'
    }).encode('utf-8')


    user2 = json.dumps({
        'email' : 'pambeesly@gmail.com',
        'password': 'jimmYHal3p',
        'name_first': 'Pamela',
        'name_last': 'Beesly'
    }).encode('utf-8')

    req1 = urllib.request.Request(f"{BASE_URL}/auth/register", data=user1, headers=HEADER)
    req2 = urllib.request.Request(f"{BASE_URL}/auth/register", data=user2, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    response2 = urllib.request.urlopen(req2)
    payload1 = json.load(response1)
    payload2 = json.load(response2)
    return payload1, payload2

@pytest.fixture
def register_two_create_public():
    user1 = json.dumps({
        'email' : 'michaelscott@gmail.com',
        'password': 'dundermifflen1',
        'name_first': 'Michael',
        'name_last': 'Scott'
    }).encode('utf-8')


    user2 = json.dumps({
        'email' : 'pambeesly@gmail.com',
        'password': 'jimmYHal3p',
        'name_first': 'Pamela',
        'name_last': 'Beesly'
    }).encode('utf-8')

    req1 = urllib.request.Request(f"{BASE_URL}/auth/register", data=user1, headers=HEADER)
    req2 = urllib.request.Request(f"{BASE_URL}/auth/register", data=user2, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    response2 = urllib.request.urlopen(req2)
    user1 = json.load(response1)
    user2 = json.load(response2)

    channel = json.dumps({
        'token' : user1['token'],
        'name': 'channel one',
        'is_public': True
    }).encode('utf-8')

    req3 = urllib.request.Request(f"{BASE_URL}/channels/create", data=channel, headers=HEADER)
    response3 = urllib.request.urlopen(req3)
    channel_id = json.load(response3)['channel_id']

    return user1, user2, channel_id


@pytest.fixture
def register_two_send_message():
    user1 = json.dumps({
        'email' : 'michaelscott@gmail.com',
        'password': 'dundermifflen1',
        'name_first': 'Michael',
        'name_last': 'Scott'
    }).encode('utf-8')


    user2 = json.dumps({
        'email' : 'pambeesly@gmail.com',
        'password': 'jimmYHal3p',
        'name_first': 'Pamela',
        'name_last': 'Beesly'
    }).encode('utf-8')

    req1 = urllib.request.Request(f"{BASE_URL}/auth/register", data=user1, headers=HEADER)
    req2 = urllib.request.Request(f"{BASE_URL}/auth/register", data=user2, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    response2 = urllib.request.urlopen(req2)
    user1 = json.load(response1)
    user2 = json.load(response2)

    channel = json.dumps({
        'token' : user1['token'],
        'name': 'channel one',
        'is_public': True
    }).encode('utf-8')

    req3 = urllib.request.Request(f"{BASE_URL}/channels/create", data=channel, headers=HEADER)
    response3 = urllib.request.urlopen(req3)
    channel_id = json.load(response3)['channel_id']

    # second user joins public channel
    channel_join = json.dumps({
        'token' : user2['token'],
        'channel_id': channel_id,
    }).encode('utf-8')

    req1 = urllib.request.Request(f"{BASE_URL}/channel/join", data=channel_join, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    json.load(response1)

    # first user sends message
    message = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
        'message': "hello world"
    }).encode('utf-8')

    req1 = urllib.request.Request(f"{BASE_URL}/message/send", data=message, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    message_id = json.load(response1)['message_id']

    return user1, user2, channel_id, message_id
