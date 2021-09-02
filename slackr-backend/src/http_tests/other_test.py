import json
import pytest
import urllib.request
import pytest
import time
from urllib.error import HTTPError, URLError
from channel_test import get_channel_details

BASE_URL = 'http://127.0.0.1:8080'
HEADER = {'Content-Type': 'application/json'}
LENGTH = 1

def check_data():
    check_data = json.load(urllib.request.urlopen(f"{BASE_URL}/check"))
    return check_data

def create_standup(token, channel_id):
    standup_details = json.dumps({
        'token' : token,
        'channel_id': channel_id,
        'length': LENGTH
    }).encode('utf-8')
    
    req1 = urllib.request.Request(f"{BASE_URL}/standup/start", data=standup_details, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    payload = json.load(response1)
    return payload

'''
Tests users/all route
'''
def test_users_all_one(register_one):
    user = register_one

    url = BASE_URL + "/users/all?token=" + user['token']
    response = urllib.request.urlopen(url)
    users = json.load(response)

    assert len(users) == 1

def test_users_all_two(register_two):
    user1, user2 = register_two

    url = BASE_URL + "/users/all?token=" + user1['token']
    response = urllib.request.urlopen(url)
    users = json.load(response)

    assert len(users['users']) == 2

'''
Tests /search route
'''
def test_search_found_one(register_two_send_message):
    fixture = register_two_send_message
    user1 = fixture[0]
    user2 = fixture[1]
    channel_id = fixture[2]
    message_id = fixture[3]

    token = 'token=' + user1['token'] + '&'
    query_str = 'query_str=Ello'
    url = BASE_URL + "/search?" + token + query_str
    response = urllib.request.urlopen(url)
    messages = json.load(response)

    assert len(messages['messages']) == 1
    assert messages['messages'][0]['message_id'] == message_id

def test_search_found_none(register_two_send_message):
    fixture = register_two_send_message
    user1 = fixture[0]
    user2 = fixture[1]
    channel_id = fixture[2]
    message_id = fixture[3]

    token = 'token=' + user1['token'] + '&'
    query_str = 'query_str=helo'
    url = BASE_URL + "/search?" + token + query_str
    response = urllib.request.urlopen(url)
    messages = json.load(response)

    assert len(messages['messages']) == 0

'''
Tests admin/user/permission route
'''
def test_admin_user_permission_change_other(register_two_create_public):
    fixture = register_two_create_public
    user1 = fixture[0]
    user2 = fixture[1]
    channel_id = fixture[2]

    change_admin = json.dumps({
        'token' : user1['token'],
        'u_id': user2['u_id'],
        'permission_id': 1
    }).encode('utf-8')

    req1 = urllib.request.Request(f"{BASE_URL}/admin/userpermission/change", data=change_admin, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    json.load(response1)

    data = check_data()
    
    assert data['profiles'][1]['is_slackr_owner'] == 1

def test_admin_user_permission_change_self(register_one):
    user = register_one

    change_admin = json.dumps({
        'token' : user['token'],
        'u_id': user['u_id'],
        'permission_id': 2
    }).encode('utf-8')

    req1 = urllib.request.Request(f"{BASE_URL}/admin/userpermission/change", data=change_admin, headers=HEADER)
    with pytest.raises(HTTPError):
        response1 = urllib.request.urlopen(req1)

def test_admin_user_permission_channel_join(register_two_create_public):
    fixture = register_two_create_public
    user1 = fixture[0]
    user2 = fixture[1]
    channel_id = fixture[2]

    change_admin = json.dumps({
        'token' : user1['token'],
        'u_id': user2['u_id'],
        'permission_id': 1
    }).encode('utf-8')
    
    req1 = urllib.request.Request(f"{BASE_URL}/admin/userpermission/change", data=change_admin, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    json.load(response1)

    # second user joins public channel and immediately becomes an owner
    channel_join = json.dumps({
        'token' : user2['token'],
        'channel_id': channel_id,
    }).encode('utf-8')

    req1 = urllib.request.Request(f"{BASE_URL}/channel/join", data=channel_join, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    json.load(response1)

    details = get_channel_details(user1['token'], channel_id)

    assert len(details['owner_members']) == 2

def test_admin_user_permission_current_channel(register_two_create_public):
    fixture = register_two_create_public
    user1 = fixture[0]
    user2 = fixture[1]
    channel_id = fixture[2]

    change_admin = json.dumps({
        'token' : user1['token'],
        'u_id': user2['u_id'],
        'permission_id': 1
    }).encode('utf-8')
 
    # second user joins public channel and immediately becomes an owner
    channel_join = json.dumps({
        'token' : user2['token'],
        'channel_id': channel_id,
    }).encode('utf-8')

    req1 = urllib.request.Request(f"{BASE_URL}/channel/join", data=channel_join, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    json.load(response1)
    
    req1 = urllib.request.Request(f"{BASE_URL}/admin/userpermission/change", data=change_admin, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    json.load(response1)

    details = get_channel_details(user1['token'], channel_id)

    assert len(details['owner_members']) == 2

'''
Test admin/user/remove route
'''
def test_admin_user_remove_other_as_owner(register_two):
    '''
    Tests an owner removing another user
    '''
    fixture = register_two
    owner = fixture[0]
    user1 = fixture[1]

    data = check_data()

    # Before remove
    assert len(data['profiles']) == 2

    remove = json.dumps({
        'token' : owner['token'],
        'u_id': user1['u_id']
    }).encode('utf-8')

    req = urllib.request.Request(f"{BASE_URL}/admin/user/remove", data=remove, headers=HEADER, method='DELETE')
    response = urllib.request.urlopen(req)
    json.load(response)

    data = check_data()

    #After Remove
    assert len(data['profiles']) == 1


def test_admin_user_remove_other_sent_messages_as_owner(register_two_create_public):
    '''
    Tests an owner removing another user after that
    user has sent a message in a channel
    '''
    fixture = register_two_create_public
    owner = fixture[0]
    user1 = fixture[1]
    channel_id = fixture[2]

    data = check_data()

    # Before remove
    assert len(data['profiles']) == 2

    # second user joins public channel
    channel_join = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
    }).encode('utf-8')

    req1 = urllib.request.Request(f"{BASE_URL}/channel/join", data=channel_join, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    json.load(response1)

    # user1 sends message
    message = json.dumps({
        'token' : user1['token'],
        'channel_id': channel_id,
        'message': "hello world"
    }).encode('utf-8')

    req1 = urllib.request.Request(f"{BASE_URL}/message/send", data=message, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    message_id = json.load(response1)['message_id']

    remove = json.dumps({
        'token' : owner['token'],
        'u_id': user1['u_id']
    }).encode('utf-8')

    req = urllib.request.Request(f"{BASE_URL}/admin/user/remove", data=remove, headers=HEADER, method='DELETE')
    response = urllib.request.urlopen(req)
    json.load(response)

    data = check_data()

    #After Remove
    assert len(data['profiles']) == 1

    assert len(data['channels'][0]['messages']) == 1

'''
Test Standup routes
'''
def test_standup_start(register_two_create_public):
    fixture = register_two_create_public
    user = fixture[0]
    channel_id = fixture[2]

    payload = create_standup(user['token'], channel_id)

    assert payload['time_finish'] == int(time.time()) + LENGTH

def test_standup_active(register_two_create_public):
    fixture = register_two_create_public
    user = fixture[0]
    user2 = fixture[1]
    channel_id = fixture[2]

    payload = create_standup(user['token'], channel_id)
    
    query_str = '?token=' + user['token'] + "&channel_id=" + str(channel_id)  
    url = BASE_URL + "/standup/active" + query_str
    response = urllib.request.urlopen(url)
    time_finish = json.load(response)['time_finish']

    assert payload['time_finish'] == time_finish

def test_standup_active_standup_ends(register_two_create_public):
    fixture = register_two_create_public
    user = fixture[0]
    user2 = fixture[1]
    channel_id = fixture[2]

    payload = create_standup(user['token'], channel_id)
        
    query_str = '?token=' + user['token'] + "&channel_id=" + str(channel_id)  
    url = BASE_URL + "/standup/active" + query_str
    response = urllib.request.urlopen(url)
    is_active = json.load(response)['is_active']

    assert is_active is True

    time.sleep(1)
    
    query_str = '?token=' + user['token'] + "&channel_id=" + str(channel_id)  
    url = BASE_URL + "/standup/active" + query_str
    response = urllib.request.urlopen(url)
    is_active = json.load(response)['is_active']

    assert is_active is False

def test_standup_send(register_two_create_public):
    fixture = register_two_create_public
    user = fixture[0]
    user2 = fixture[1]
    channel_id = fixture[2]

    create_standup(user['token'], channel_id)
        
    standup_details = json.dumps({
        'token' : user['token'],
        'channel_id': channel_id,
        'message': 'Dunder Mifflin Paper Company Standup'
    }).encode('utf-8')
    
    req1 = urllib.request.Request(f"{BASE_URL}/standup/send", data=standup_details, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    payload = json.load(response1)
    
    time.sleep(LENGTH)
    data = check_data()['channels'][0]

    assert data['messages'][0]['message'] == "Michael: Dunder Mifflin Paper Company Standup"
