import pytest
from error import InputError, AccessError
from auth import auth_register, auth_logout
from user import user_profile
from server import reset_req

@pytest.fixture(autouse=True)
def reset_state():
    reset_req()

def test_user_valid():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    profile = user_profile(user['token'], user['u_id'])
    
    assert profile['user']['u_id'] == user['u_id']

def test_user_invalid_ID():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    
    with pytest.raises(InputError):
        user_profile(user['token'], user['u_id']*2)

def test_user_invalid_token():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    auth_logout(user['token'])
    
    with pytest.raises(AccessError):
        user_profile(user['token'], user['u_id'])

def test_user_short_name():
    user = auth_register('ba@gmail.com', '#abc123', 'B', 'A')
    profile = user_profile(user['token'], user['u_id'])['user']
    
    assert profile['handle_str'] == 'ba'

def test_user_long_name():
    user = auth_register('bobA@gmail.com', '#abc123', 'Bob', 'A' * 30)
    profile = user_profile(user['token'], user['u_id'])['user']
    
    assert profile['handle_str'] == 'b' + 'a' * 19

def test_user_same_short_name():
    user = auth_register('ba@gmail.com', '#abc123', 'B', 'A')
    user2 = auth_register('baa@gmail.com', '#def456', 'B', 'A')
    profile = user_profile(user2['token'], user2['u_id'])['user'] 
    
    assert profile['handle_str'] == 'ba1'

def test_user_similar_long_name():
    auth_register('bobA@gmail.com', '#abc123', 'Bob', 'A' * 19)
    user2 = auth_register('barbA@gmail.com', '#def456', 'Barb', 'A' * 19)
    profile = user_profile(user2['token'], user2['u_id'])['user']
    
    assert profile['handle_str'] == 'b' + 'a' * 18 + '1'
