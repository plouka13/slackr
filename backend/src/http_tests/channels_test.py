import json
import pytest
import urllib.request
# from error import InputError

BASE_URL = 'http://127.0.0.1:8080'
HEADER = {'Content-Type': 'application/json'}


def check_data():
    check_data = json.load(urllib.request.urlopen(f"{BASE_URL}/check"))
    return check_data

def test_channels_create_public(register_two):
    user1, user2 = register_two

    channel = json.dumps({
        'token' : user1['token'],
        'name': 'channel one',
        'is_public': True
    }).encode('utf-8')

    req1 = urllib.request.Request(f"{BASE_URL}/channels/create", data=channel, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    channel_payload = json.load(response1)['channel_id']

    all_data = check_data()

    assert channel_payload == all_data['channels'][0]['channel_id']


def test_channels_create_two_private(register_two):
    user1, user2 = register_two

    channel = json.dumps({
        'token' : user2['token'],
        'name': 'a' * 20,
        'is_public': False
    }).encode('utf-8')

    req1 = urllib.request.Request(f"{BASE_URL}/channels/create", data=channel, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    channel_payload = json.load(response1)['channel_id']

    req2 = urllib.request.Request(f"{BASE_URL}/channels/create", data=channel, headers=HEADER)
    response2 = urllib.request.urlopen(req2)
    channel_payload2 = json.load(response2)['channel_id']

    all_data = check_data()

    assert channel_payload == all_data['channels'][0]['channel_id']
    assert channel_payload2 == all_data['channels'][1]['channel_id']

# def test_channels_create_name_too_long(register_one):
#     user = register_one
#     channel = json.dumps({
#         'token' : user['token'],
#         'name': 'a'*21,
#         'is_public': True
#     }).encode('utf-8')
#     req1 = urllib.request.Request(f"{BASE_URL}/channels/create", data=channel, headers=HEADER)
    
#     with pytest.raises(InputError):
#         response1 = urllib.request.urlopen(req1)


def test_channels_list(register_two):
    user1, user2 = register_two
    channel = json.dumps({
        'token' : user1['token'],
        'name': 'a' * 20,
        'is_public': False
    }).encode('utf-8')

    req1 = urllib.request.Request(f"{BASE_URL}/channels/create", data=channel, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    channel_payload = json.load(response1)

    all_data = check_data()
    assert len(all_data['channels'][0]['all_members']) == 1

    url2 = BASE_URL + "/channels/list?token=" + user1['token']
    response2 = urllib.request.urlopen(url2)
    channel_payload2 = json.load(response2)['channels']

    assert len(channel_payload2) == 1

    url3 = BASE_URL + "/channels/list?token=" + user2['token']
    response3 = urllib.request.urlopen(url3)
    channel_payload3 = json.load(response3)['channels']

    assert len(channel_payload3) == 0


def test_channels_listall(register_two):
    user1, user2 = register_two
    channel = json.dumps({
        'token' : user1['token'],
        'name': 'a' * 20,
        'is_public': False
    }).encode('utf-8')

    req1 = urllib.request.Request(f"{BASE_URL}/channels/create", data=channel, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    channel_payload = json.load(response1)

    all_data = check_data()
    assert len(all_data['channels'][0]['all_members']) == 1

    # req2 = urllib.request.Request(f"{BASE_URL}/channels/list")
    url2 = BASE_URL + "/channels/listall?token=" + user1['token']
    response2 = urllib.request.urlopen(url2)
    channel_payload2 = json.load(response2)

    assert len(channel_payload2) == 1

    url3 = BASE_URL + "/channels/listall?token=" + user2['token']
    response3 = urllib.request.urlopen(url3)
    channel_payload3 = json.load(response3)

    assert len(channel_payload3) == 1





