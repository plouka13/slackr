import json
import pytest
import urllib.request

BASE_URL = 'http://127.0.0.1:8080'
HEADER = {'Content-Type': 'application/json'}

def check_data():
    check_data = json.load(urllib.request.urlopen(f"{BASE_URL}/check"))
    return check_data

'''
Tests workspace/reset route
'''
def test_reset_empty():

    # Reset
    DATA = ''.encode('utf-8')
    REQ = urllib.request.Request(f"{BASE_URL}/workspace/reset", data=DATA, headers=HEADER)
    urllib.request.urlopen(REQ)
    PAYLOAD = json.load(urllib.request.urlopen(f"{BASE_URL}/check"))

    assert PAYLOAD == {
            'profiles': [],
            'users': [],
            'logged_in': [],
            'channels': [],
            'standups': [],
            'total_messages': 0,
            'img_count': 0
        }

def test_auth_register_one(register_one):
    payload = register_one

    total_data = check_data()

    # check = check_data()
    # assert len(check) == 4
    assert payload['u_id'] == total_data['users'][0]['u_id']
    assert len(total_data['profiles']) == 1
    assert len(total_data['users']) == 1
    assert len(total_data['logged_in']) == 1
    assert total_data['users'][0]['email'] == 'michaelscott@gmail.com'

  

def test_auth_register_two(register_two):
    payload1, payload2 = register_two
    total_data = check_data()
    assert payload1['u_id'] == total_data['users'][0]['u_id']
    assert payload2['u_id'] == total_data['users'][1]['u_id']

    assert len(total_data['profiles']) == 2
    assert len(total_data['users']) == 2
    assert len(total_data['logged_in']) == 2

def test_auth_logout_success(register_two):
    payload1, payload2 = register_two
    token1 = payload1['token']

    data = json.dumps({
    'token': token1
    }).encode('utf-8')

    req = urllib.request.Request(f"{BASE_URL}/auth/logout", data=data, headers=HEADER)
    response = urllib.request.urlopen(req)
    payload = json.load(response)

    assert payload
    total_data = check_data()

    assert len(total_data['profiles']) == 2
    assert len(total_data['users']) == 2
    assert len(total_data['logged_in']) == 1

def test_auth_logout_success_two(register_two):
    payload1, payload2 = register_two

    data1 = json.dumps({
    'token': payload1['token']
    }).encode('utf-8')
    data2 = json.dumps({
    'token': payload2['token']
    }).encode('utf-8')

    req1 = urllib.request.Request(f"{BASE_URL}/auth/logout", data=data1, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    payload1 = json.load(response1)
    assert payload1

    req2 = urllib.request.Request(f"{BASE_URL}/auth/logout", data=data2, headers=HEADER)

    response2 = urllib.request.urlopen(req2)
    payload2 = json.load(response2)

    assert payload2
    total_data = check_data()

    assert len(total_data['profiles']) == 2
    assert len(total_data['users']) == 2
    assert len(total_data['logged_in']) == 0


def test_auth_logout_login_success_two(register_two):
    payload1, payload2 = register_two

    data1 = json.dumps({
    'token': payload1['token']
    }).encode('utf-8')
    data2 = json.dumps({
    'token': payload2['token']
    }).encode('utf-8')

    req1 = urllib.request.Request(f"{BASE_URL}/auth/logout", data=data1, headers=HEADER)
    response1 = urllib.request.urlopen(req1)
    req2 = urllib.request.Request(f"{BASE_URL}/auth/logout", data=data2, headers=HEADER)
    response2 = urllib.request.urlopen(req2)

    data3 = json.dumps({
    'email': 'michaelscott@gmail.com',
    'password': 'dundermifflen1'
    }).encode('utf-8')
    data4 = json.dumps({
    'email': 'pambeesly@gmail.com',
    'password': 'jimmYHal3p'
    }).encode('utf-8')

    req3 = urllib.request.Request(f"{BASE_URL}/auth/login", data=data3, headers=HEADER)
    req4 = urllib.request.Request(f"{BASE_URL}/auth/login", data=data4, headers=HEADER)
    response3 = urllib.request.urlopen(req3)
    response4 = urllib.request.urlopen(req4)


    total_data = check_data()

    assert len(total_data['profiles']) == 2
    assert len(total_data['users']) == 2
    assert len(total_data['logged_in']) == 2



# print('''After:
#     Registering Michael Scott and Pamela Beesly,
#     Logging out Michael Scott and Pamela Beesly,
#     Logging in Michael Scott
#     The DATA structure looks as follows
# __________________________________________________''')
# print(json.dumps(PAYLOAD, indent=4))
