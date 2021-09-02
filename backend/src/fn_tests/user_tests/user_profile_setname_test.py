import pytest
from error import InputError, AccessError
from auth import auth_register, auth_logout
from user import user_profile, user_profile_setname
from server import reset_req

@pytest.fixture(autouse=True)
def reset_state():
    reset_req()

def test_profile_setname_valid():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_setname(user['token'], 'Bo', 'Smith')    
    user2 = user_profile(user['token'], user['u_id'])['user']
    
    assert user2['name_first'] == 'Bo'
    assert user2['name_last'] == 'Smith'
 
def test_profile_setname_valid_min_first():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_setname(user['token'], 'B', 'Smith')    
    user2 = user_profile(user['token'], user['u_id'])['user'] 
    
    assert user2['name_first'] == 'B'
    assert user2['name_last'] == 'Smith'
 
def test_profile_setname_valid_min_last():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_setname(user['token'], 'Bob', 'S')    
    user2 = user_profile(user['token'], user['u_id'])['user']
    
    assert user2['name_first'] == 'Bob'
    assert user2['name_last'] == 'S'
 
def test_profile_setname_valid_max_first():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_setname(user['token'], 'B'*50, 'Smith')    
    user2 = user_profile(user['token'], user['u_id'])['user']
    
    assert user2['name_first'] == 'B'*50
    assert user2['name_last'] == 'Smith'
 
def test_profile_setname_valid_max_last():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_setname(user['token'], 'Bob', 'S'*50)    
    user2 = user_profile(user['token'], user['u_id'])['user']
    
    assert user2['name_first'] == 'Bob'
    assert user2['name_last'] == 'S'*50

def test_profile_setname_valid_hyphen_character():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_setname(user['token'], 'Bob', 'Smith-Jones')
    user2 = user_profile(user['token'], user['u_id'])['user'] 
    
    assert user2['name_first'] == 'Bob'
    assert user2['name_last'] == 'Smith-Jones'

def test_profile_setname_valid_apostrophe_character():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_setname(user['token'], 'Bob', 'O\'Brian')
    user2 = user_profile(user['token'], user['u_id'])['user'] 
    
    assert user2['name_first'] == 'Bob'
    assert user2['name_last'] == 'O\'Brian'

def test_profile_setname_valid_space_character():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user_profile_setname(user['token'], 'Bob', 'von Braun')
    user2 = user_profile(user['token'], user['u_id'])['user'] 
    
    assert user2['name_first'] == 'Bob'
    assert user2['name_last'] == 'von Braun'
 
def test_profile_setname_invalid_token():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    auth_logout(user['token'])
    
    with pytest.raises(AccessError):
        user_profile_setname(user['token'], 'Bo', 'S')

def test_profile_setname_invalid_characters_exclamation():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    
    with pytest.raises(InputError):
        user_profile_setname(user['token'], 'Bob', '!')

def test_profile_setname_invalid_characters_at():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    with pytest.raises(InputError):
        user_profile_setname(user['token'], 'Bob', '@')

def test_profile_setname_invalid_characters_period():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    with pytest.raises(InputError):
        user_profile_setname(user['token'], 'Bob', '.')

def test_profile_setname_invalid_characters_comma():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    
    with pytest.raises(InputError):
        user_profile_setname(user['token'], 'Bob', ',')

def test_profile_setname_invalid_characters_pound():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    
    with pytest.raises(InputError):
        user_profile_setname(user['token'], 'Bob', '#')

def test_profile_setname_invalid_characters_dollar():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    
    with pytest.raises(InputError):
         user_profile_setname(user['token'], 'Bob', '$')

def test_profile_setname_invalid_characters_percent():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    
    with pytest.raises(InputError):
        user_profile_setname(user['token'], 'Bob', '%')

def test_profile_setname_invalid_characters_carat():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    
    with pytest.raises(InputError):
        user_profile_setname(user['token'], 'Bob', '^')

def test_profile_setname_invalid_characters_ampersand():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    
    with pytest.raises(InputError):
        user_profile_setname(user['token'], 'Bob', '&')

def test_profile_setname_invalid_characters_asterisk():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    with pytest.raises(InputError):
        user_profile_setname(user['token'], 'Bob', '*')

def test_profile_setname_invalid_characters_brackets():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    with pytest.raises(InputError):
        user_profile_setname(user['token'], 'Bob', '()')

def test_profile_setname_last_trailing_spaces():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    user_profile_setname(user['token'], 'Bob', 'Smith   ')
    user2 = user_profile(user['token'], user['u_id'])['user']
    assert user2['name_first'] == 'Bob'
    assert user2['name_last'] == 'Smith'

def test_profile_setname_last_leading_spaces():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    user_profile_setname(user['token'], 'Bob', '   Smith')
    user2 = user_profile(user['token'], user['u_id'])['user']
    assert user2['name_first'] == 'Bob'
    assert user2['name_last'] == 'Smith'

def test_profile_setname_first_trailing_spaces():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    user_profile_setname(user['token'], 'Bob   ', 'Smith')
    user2 = user_profile(user['token'], user['u_id'])['user']
    assert user2['name_first'] == 'Bob'
    assert user2['name_last'] == 'Smith'

def test_profile_setname_first_leading_spaces():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    user_profile_setname(user['token'], '   Bob', 'Smith')
    user2 = user_profile(user['token'], user['u_id'])['user']
    assert user2['name_first'] == 'Bob'
    assert user2['name_last'] == 'Smith'

def test_profile_setname_large_leading_spaces_first():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    user_profile_setname(user['token'], 'Bob' + ' '*50, 'Smiths')
    user2 = user_profile(user['token'], user['u_id'])['user']
    assert user2['name_first'] == 'Bob'
    assert user2['name_last'] == 'Smiths'

def test_profile_setname_large_trailing_spaces():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    user_profile_setname(user['token'], 'Bob', 'Smiths' + ' '*50)
    user2 = user_profile(user['token'], user['u_id'])['user']
    assert user2['name_first'] == 'Bob'
    assert user2['name_last'] == 'Smiths'
    
def test_profile_setname_invalid_large_first():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    with pytest.raises(InputError):
        user_profile_setname(user['token'], 'B'*51, 'Smith')  
    
def test_profile_setname_invalid_large_last():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    with pytest.raises(InputError):
        user_profile_setname(user['token'], 'Bob', 'S'*51)  
 
def test_profile_setname_invalid_empty_first():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    with pytest.raises(InputError):
        user_profile_setname(user['token'], '', 'Smith')    
 
def test_profile_setname_invalid_empty_last():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    with pytest.raises(InputError):
        user_profile_setname(user['token'], 'Bob', '')
        
def test_profile_setname_spaces_first():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    with pytest.raises(InputError):
        user_profile_setname(user['token'], '    ', 'Smith')
 
def test_profile_setname_spaces_last():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    
    with pytest.raises(InputError):
        user_profile_setname(user['token'], 'Bob', '    ')
 
def test_profile_setname_numbers_last():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    with pytest.raises(InputError):
        user_profile_setname(user['token'], 'Bob', '123')
 
def test_profile_setname_partial_numbers_first():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    with pytest.raises(InputError):
        user_profile_setname(user['token'], 'Bob123', 'Smith')    
 
def test_profile_setname_partial_numbers_last():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    with pytest.raises(InputError):
        user_profile_setname(user['token'], 'Bob', 'Smith123') 
 
def test_profile_setname_invalid_first():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    with pytest.raises(InputError):
        user_profile_setname(user['token'], '000', 'S')   
 
def test_profile_setname_invalid_last():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    with pytest.raises(InputError):
        user_profile_setname(user['token'], 'Bobby', 'Smith123')   

