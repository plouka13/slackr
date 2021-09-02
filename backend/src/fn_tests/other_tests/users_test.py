import pytest
from error import InputError, AccessError
from auth import auth_logout, auth_register
from other import users_all
from user import user_profile_setname, user_profile_setemail, user_profile_sethandle 
from server import reset_req

@pytest.fixture(autouse=True)
def reset_state():
    reset_req()

def test_users_invalid_token(register_one):
    u_id, token  = register_one
    auth_logout(token)
    with pytest.raises(AccessError):
        users_all(token)

def test_users_one(register_one):
    u_id, token  = register_one
    users = users_all(token)['users']
    assert len(users) == 1
    
def test_users_two(): 
    user1 = auth_register('bobsmith123@gmail.com', '#abc123', 
    'Bob', 'Smith')
    user2  = auth_register('bsmith99@gmail.com', '#def456', 
    'Barbara', 'Smith')

    users = users_all(user1['token'])['users'] 
    assert len(users) == 2
