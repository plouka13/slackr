import pytest
from auth import auth_register, auth_login, auth_logout
from error import AccessError
from server import reset_req

@pytest.fixture(autouse=True)
def reset_state():
    reset_req()

def test_logout_success():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    assert auth_logout(user['token'])

def test_logout_success_repeat():
    user1 = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_register('brucejones@aol.com', 'xyz789!', 'Bruce', 'Jones')
    assert auth_logout(user1['token'])
    assert auth_logout(user2['token'])

def test_logout_success_repeat_same():
    user1 = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    assert auth_logout(user1['token'])

    user2 = auth_login('bobsmith123@gmail.com', '#abc123')
    assert user1['u_id'] == user2['u_id']
    assert auth_logout(user2['token'])

def test_logout_failure_repeat():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    auth_logout(user['token'])
    with pytest.raises(AccessError):
        auth_logout(user['token'])
