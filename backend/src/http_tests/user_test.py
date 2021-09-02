import json
import pytest
import urllib.request
import pytest
from error import InputError
from urllib.error import HTTPError, URLError

BASE_URL = 'http://127.0.0.1:8080'
HEADER = {'Content-Type': 'application/json'}

def get_user_profile(user):
    
    url_parameters = '?token=' + user['token'] + '&' + 'u_id=' + str(user['u_id'])
    
    url = BASE_URL + "/user/profile" + url_parameters
    response = urllib.request.urlopen(url)
    profile = json.load(response)

    return profile['user']

'''
User/profile route tests
'''
def test_user_profile_success_self(register_one):
    user = register_one
    url_parameters = '?token=' + user['token'] + '&' + 'u_id=' + str(user['u_id'])
    
    url = BASE_URL + "/user/profile" + url_parameters
    response = urllib.request.urlopen(url)
    profile = json.load(response)['user']

    assert profile == {'u_id': 1,
                       'email' : 'michaelscott@gmail.com',
                       'name_first': 'Michael',
                       'name_last': 'Scott',
                       'handle_str': 'mscott'}

def test_user_profile_success_different_user(register_two):
    
    user1, user2 = register_two
    url_parameters = '?token=' + user1['token'] + '&' + 'u_id=' + str(user2['u_id'])
    
    url = BASE_URL + "/user/profile" + url_parameters
    response = urllib.request.urlopen(url)
    profile = json.load(response)['user']

    assert profile == {'u_id': 2,
                       'email' : 'pambeesly@gmail.com',
                       'name_first': 'Pamela',
                       'name_last': 'Beesly',
                       'handle_str': 'pbeesly'}

def test_user_profile_invalid_id(register_one):
    
    user = register_one
    url_parameters = '?token=' + user['token'] + '&' + 'u_id=' + '0'
    
    url = BASE_URL + "/user/profile" + url_parameters
    with pytest.raises(HTTPError):
        response = urllib.request.urlopen(url)

def test_user_profile_nonexistant_user(register_one):
    
    user = register_one
    url_parameters = '?token=' + user['token'] + '&' + 'u_id=' + '2'
    
    url = BASE_URL + "/user/profile" + url_parameters
    with pytest.raises(HTTPError):
        response = urllib.request.urlopen(url)
        
'''
User/profile/setname route tests
'''

def test_user_profile_setname_valid_entry(register_one):
    
    user = register_one
    
    name_change = json.dumps({
        'token' : user['token'],
        'name_first': 'Mike',
        'name_last': 'Sco'
    }).encode('utf-8')

    req = urllib.request.Request(f"{BASE_URL}/user/profile/setname", 
                                  data=name_change, 
                                  headers=HEADER,
                                  method='PUT')
    response = urllib.request.urlopen(req)
    json.load(response)
    
    profile = get_user_profile(user)
    assert profile['name_first'] == 'Mike'
    assert profile['name_last'] == 'Sco'

def test_user_profile_setname_empty_entries(register_one):
    
    user = register_one
    
    name_change1 = json.dumps({
        'token' : user['token'],
        'name_first': '       ',
        'name_last': 'Scott'
    }).encode('utf-8')

    req = urllib.request.Request(f"{BASE_URL}/user/profile/setname", 
                                 data=name_change1, 
                                 headers=HEADER,
                                 method='PUT')
    with pytest.raises(HTTPError):
        response = urllib.request.urlopen(req)
    
    name_change2 = json.dumps({
        'token' : user['token'],
        'name_first': 'Michael',
        'name_last': '        '
    }).encode('utf-8')

    req = urllib.request.Request(f"{BASE_URL}/user/profile/setname", 
                                 data=name_change2, 
                                 headers=HEADER,
                                 method='PUT')
    with pytest.raises(HTTPError):
        response = urllib.request.urlopen(req)

def test_user_profile_setname_long_entries(register_one):
    
    user = register_one
    
    name_change1 = json.dumps({
        'token' : user['token'],
        'name_first': 'M'*51,
        'name_last': 'Scott'
    }).encode('utf-8')

    req = urllib.request.Request(f"{BASE_URL}/user/profile/setname", 
                                 data=name_change1, 
                                 headers=HEADER,
                                 method='PUT')
    with pytest.raises(HTTPError):
        response = urllib.request.urlopen(req)

    name_change2 = json.dumps({
        'token' : user['token'],
        'name_first': 'Michael',
        'name_last': 'S'*51
    }).encode('utf-8')

    req = urllib.request.Request(f"{BASE_URL}/user/profile/setname", 
                                 data=name_change2, 
                                 headers=HEADER,
                                  method='PUT')
    with pytest.raises(HTTPError):
        response = urllib.request.urlopen(req)

def test_user_profile_invalid_token(register_one):
    
    user = register_one
    
    name_change1 = json.dumps({
        'token' : 12345,
        'name_first': 'M'*51,
        'name_last': 'Scott'
    }).encode('utf-8')

    req = urllib.request.Request(f"{BASE_URL}/user/profile/setname", 
                                 data=name_change1, 
                                headers=HEADER,
                                method='PUT')
    with pytest.raises(HTTPError):
        response = urllib.request.urlopen(req)
    
'''
user/profile/setemail tests
'''
def test_user_profile_setemail_success(register_one):
    
    user = register_one
    
    name_change1 = json.dumps({
        'token' : user['token'],
        'email': 'mscott@hotmail.com',
    }).encode('utf-8')

    req = urllib.request.Request(f"{BASE_URL}/user/profile/setemail", 
                                 data=name_change1, 
                                 headers=HEADER,
                                 method='PUT')
    
    response = urllib.request.urlopen(req)
    json.load(response)
    
    profile = get_user_profile(user)
    assert profile['email'] == 'mscott@hotmail.com'

def test_user_profile_setemail_taken(register_one):
    
    user = register_one
    
    name_change1 = json.dumps({
        'token' : user['token'],
        'email': 'michaelscott@gmail.com',
    }).encode('utf-8')

    req = urllib.request.Request(f"{BASE_URL}/user/profile/setemail", 
                                 data=name_change1, 
                                 headers=HEADER,
                                 method='PUT')
    with pytest.raises(HTTPError):
        response = urllib.request.urlopen(req)

def test_user_profile_setemail_invalid_email(register_one):
    
    user = register_one
    
    name_change1 = json.dumps({
        'token' : user['token'],
        'email': 'michaelscottgmailcom',
    }).encode('utf-8')

    req = urllib.request.Request(f"{BASE_URL}/user/profile/setemail", 
                                 data=name_change1, 
                                 headers=HEADER,
                                 method='PUT')
    with pytest.raises(HTTPError):
        response = urllib.request.urlopen(req)

'''
User/profile/sethandle tests
'''
def test_user_profile_handle_valid(register_one):
    
    user = register_one
    
    name_change1 = json.dumps({
        'token' : user['token'],
        'handle_str': 'scotterminator',
    }).encode('utf-8')

    req = urllib.request.Request(f"{BASE_URL}/user/profile/sethandle", 
                                 data=name_change1, 
                                 headers=HEADER,
                                 method='PUT')
    response = urllib.request.urlopen(req)
    json.load(response)

    profile = get_user_profile(user)
    assert profile['handle_str'] == 'scotterminator'
    
def test_user_profile_handle_taken(register_two):
    
    user1, user2 = register_two
    
    name_change1 = json.dumps({
        'token' : user1['token'],
        'handle_str': 'pbeesly',
    }).encode('utf-8')

    req = urllib.request.Request(f"{BASE_URL}/user/profile/sethandle", 
                                 data=name_change1, 
                                 headers=HEADER,
                                 method='PUT')
    with pytest.raises(HTTPError):
        response = urllib.request.urlopen(req)

def test_user_profile_handle_invalid_token(register_two):
    
    user1, user2 = register_two
    
    name_change1 = json.dumps({
        'token' : 123,
        'handle_str': 'mscotts',
    }).encode('utf-8')

    req = urllib.request.Request(f"{BASE_URL}/user/profile/sethandle", 
                                 data=name_change1, 
                                 headers=HEADER,
                                 method='PUT')
    with pytest.raises(HTTPError):
        response = urllib.request.urlopen(req)
     
