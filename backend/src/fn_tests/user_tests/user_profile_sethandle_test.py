import pytest
from error import InputError, AccessError
from auth import auth_logout, auth_register
from user import user_profile, user_profile_sethandle
from server import reset_req

@pytest.fixture(autouse=True)
def reset_state():
    reset_req()

def test_profile_sethandle_valid():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_sethandle(user['token'], 'bosmith')
    user2 = user_profile(user['token'], user['u_id'])['user']
    assert user2['handle_str'] == 'bosmith'

def test_profile_sethandle_min():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_sethandle(user['token'], 'bos')
    user2 = user_profile(user['token'], user['u_id'])['user']
    assert user2['handle_str'] == 'bos'

def test_profile_sethandle_max():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_sethandle(user['token'], 'b'*20)
    user2 = user_profile(user['token'], user['u_id'])['user']
    assert user2['handle_str'] == 'b'*20

def test_profile_sethandle_digits():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_sethandle(user['token'], '123456')
    user2 = user_profile(user['token'], user['u_id'])['user']
    assert user2['handle_str'] == '123456'

def test_profile_sethandle_capitals():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_sethandle(user['token'], 'BOBSMITH')
    user2 = user_profile(user['token'], user['u_id'])['user']
    assert user2['handle_str'] == 'BOBSMITH'

def test_profile_sethandle_special_characters():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_sethandle(user['token'], '!@#$%^&*()')
    user2 = user_profile(user['token'], user['u_id'])['user']
    assert user2['handle_str'] == '!@#$%^&*()'

def test_user_invalid_token():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    auth_logout(user['token'])
    with pytest.raises(AccessError):
        user_profile(user['token'], user['u_id'])

def test_profile_sethandle_long():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    with pytest.raises(InputError):
        user_profile_sethandle(user['token'], 'B'*21)
 
def test_profile_sethandle_short():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    with pytest.raises(InputError):
        user_profile_sethandle(user['token'], 'B')

def test_profile_sethandle_empty():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    with pytest.raises(InputError):
        user_profile_sethandle(user['token'], '')   

def test_profile_sethandle_all_spaces():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    with pytest.raises(InputError):
        user_profile_sethandle(user['token'], '     ') 

def test_profile_sethandle_leading_spaces():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_sethandle(user['token'], '  Bob') 
    user2 = user_profile(user['token'], user['u_id'])['user']
    assert user2['handle_str'] == 'Bob'

def test_profile_sethandle_trailing_spaces():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_sethandle(user['token'], 'Bob  ') 
    user2 = user_profile(user['token'], user['u_id'])['user']
    assert user2['handle_str'] == 'Bob'

def test_profile_sethandle_trailing_leading_spaces():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_sethandle(user['token'], '  Bob  ') 
    user2 = user_profile(user['token'], user['u_id'])['user']
    assert user2['handle_str'] == 'Bob' 

def test_profile_sethandle_spaces_outside_max():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_sethandle(user['token'], 'Bob' + ' '*20) 
    user2 = user_profile(user['token'], user['u_id'])['user']
    assert user2['handle_str'] == 'Bob'
       
def test_profile_sethandle_newly_taken():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_sethandle(user['token'], 'bsmit') 
    user2 = auth_register('bsmith@gmail.com', '#abc123', 'Barbara', 'Smit')
    user3 = user_profile(user2['token'], user2['u_id'])['user'] 
    assert user3['handle_str'] == 'bsmit1'   

def test_profile_sethandle_newly_changed():
    user1 = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_register('bsmith@gmail.com', '#abc123', 'Barbara', 'Smit')
    user_profile_sethandle(user1['token'], 'BSmi')
    with pytest.raises(InputError):
        user_profile_sethandle(user2['token'], 'BSmi')  
       
def test_profile_sethandle_previously_taken():
    user1 = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_sethandle(user1['token'], 'bsmit') 
    user2 = auth_register('bsmith@gmail.com', '#abc123', 'Barbara', 'Smit')
    user3 = user_profile(user2['token'], user2['u_id'])['user'] 
    assert user3['handle_str'] == 'bsmit1'  
       
def test_profile_sethandle_taken():
    user1 = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_register('bsmith@gmail.com', '#abc123', 'Barbara', 'Smit')
    with pytest.raises(InputError):
        user_profile_sethandle(user1['token'], 'bsmit')    

def test_profile_sethandle_taken_capitals():
    user1 = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_register('bsmith@gmail.com', '#abc123', 'Barbara', 'Smit')
    with pytest.raises(InputError):
        user_profile_sethandle(user1['token'], 'BSMIT') 
