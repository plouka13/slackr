import pytest
from error import InputError, AccessError
from auth import auth_logout, auth_register
from user import user_profile, user_profile_setemail
from server import reset_req

@pytest.fixture(autouse=True)
def reset_state():
    reset_req()

def test_profile_setemail_invalid_token():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    auth_logout(user['token'])
    with pytest.raises(AccessError):
        user_profile_setemail(user['token'], 'bobsmith1234@gmail.com')

def test_profile_setemail_valid_test1():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_setemail(user['token'], 'bobsmith1234@gmail.com')
    user2 = user_profile(user['token'], user['u_id'])['user']
    assert user2['email'] == 'bobsmith1234@gmail.com'

def test_profile_setemail_valid_test2():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_setemail(user['token'], 'bob.smith1234@gmail.com')
    user2 = user_profile(user['token'], user['u_id'])['user']
    assert user2['email'] == 'bob.smith1234@gmail.com'

def test_profile_setemail_valid_test3():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_setemail(user['token'], 'bob__smith1234@gmail.com')
    user2 = user_profile(user['token'], user['u_id'])['user']
    assert user2['email'] == 'bob__smith1234@gmail.com'

def test_profile_setemail_invalid_test1():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], 'bobsmith123gmail.com')

def test_profile_setemail_invalid_test2():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], 'bobsmith1234@gmail')

def test_profile_setemail_invalid_test3():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], 'bob..smith1234@gmail.com')

def test_profile_setemail_empty():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], '')

def test_profile_setemail_taken():
    user1 = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    auth_register('bsmith@gmail.com', '#abc123', 'Barbara', 'Smith')
    with pytest.raises(InputError):
        user_profile_setemail(user1['token'], 'bsmith@gmail.com')

def test_profile_setemail_taken_capitalized():
    user1 = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    auth_register('bsmith@gmail.com', '#abc123', 'Barbara', 'Smith')
    with pytest.raises(InputError):
        user_profile_setemail(user1['token'], 'BSMITH@gmail.com')
