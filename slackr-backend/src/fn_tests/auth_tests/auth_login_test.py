import pytest
from error import InputError
from auth import auth_login, auth_register, auth_logout
from server import reset_req

@pytest.fixture(autouse=True)
def reset_state():
    reset_req()

def test_login_two_sessions():
    user1 = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_login('bobsmith123@gmail.com', '#abc123')

    assert user1['token'] == user2['token']
    assert user1['u_id'] == user2['u_id']

def test_login_double():
    user1 = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_login('bobsmith123@gmail.com', '#abc123')
    user3 = auth_register('brucejones@aol.com', 'xyz789!', 'Bruce', 'Jones')
    user4 = auth_login('brucejones@aol.com', 'xyz789!')

    assert user1['token'] == user2['token']
    assert user1['u_id'] == user2['u_id']
    assert user3['token'] == user4['token']
    assert user3['u_id'] == user4['u_id']

def test_register_logout_login():
    user1 = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    auth_logout(user1['token'])
    user2 = auth_login('bobsmith123@gmail.com', '#abc123')

    assert user1['u_id'] == user2['u_id']


def test_login_invalid_email():
    with pytest.raises(InputError):
        auth_login('bobsmith123.com', '#abc123')

def test_login_no_such_user():
    auth_register('bobsmith@gmail.com', '#abc123', 'Bob', 'Smith')
    auth_register('janesmith@gmail.com', '#abc123', 'Jane', 'Smith')
    with pytest.raises(InputError):
        auth_login('noemail@gmail.com', '#abc123')

def test_login_invalid_password():
    auth_register('bobsmith@gmail.com', '#abc123', 'Bob', 'Smith')
    with pytest.raises(InputError):
        auth_login('bobsmith@gmail.com', '#aBc123')

def test_login_empty_password():
    auth_register('bobsmith@gmail.com', '#abc123', 'Bob', 'Smith')
    with pytest.raises(InputError):
        auth_login('bobsmith@gmail.com', '')

def test_login_empty_email():
    auth_register('bobsmith@gmail.com', '#abc123', 'Bob', 'Smith')
    with pytest.raises(InputError):
        auth_login('', '#aBc123')
