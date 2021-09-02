import pytest
from error import InputError
from auth import auth_register
from server import reset_req

@pytest.fixture(autouse=True)
def reset_state():
    reset_req()

def test_register_valid():
    auth_register('bobsmith@gmail.com', '#abc123', 'Bob', 'Smith')

def test_register_same_handle():
    user1 = auth_register('bobsmith@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_register('bobsmith123@gmail.com', '#abc123', 'carsen', 'Smith')
    assert user1['token'] != user2['token']
    assert user1['u_id'] != user2['u_id']

def test_register_min_first_name():
    auth_register('bobsmith@gmail.com', '#abc123', 'B', 'Smith')

def test_register_min_last_name():
    auth_register('bobsmith@gmail.com', '#abc123', 'Bob', 'S')

def test_register_max_first_name():
    auth_register('bobsmith@gmail.com', '#abc123', 'B'*50, 'Smith')

def test_register_max_last_name():
    auth_register('bobsmith@gmail.com', '#abc123', 'Bob', 'S'*50)

def test_register_long_handle():
    auth_register('bobsmith@gmail.com', '#abc123', 'A'*21, 'Smith')

def test_register_same_long_handle():
    user1 = auth_register('bobsmith@gmail.com', '#abc123', 'A'*21, 'B'*5)
    user2 = auth_register('bobsmith123@gmail.com', '#abc123', 'A'*21, 'B'*5)
    assert user1['token'] != user2['token']
    assert user1['u_id'] != user2['u_id']

def test_register_invalid_email():
    with pytest.raises(InputError):
        auth_register('bobsmith123.com', '#abc123', 'Bob', 'Smith')

def test_register_repeat_user():
    auth_register('bobsmith@gmail.com', '#abc123', 'Bob', 'Smith')
    with pytest.raises(InputError):
        auth_register('bobsmith@gmail.com', '#abc123', 'Mary', 'Smith')

def test_register_short_password():
    with pytest.raises(InputError):
        auth_register('bobsmith123@gmail.com', '#abc1', 'Bob', 'Smith')

def test_register_no_password():
    with pytest.raises(InputError):
        auth_register('bobsmith123@gmail.com', '', 'Bob', 'Smith')

def test_register_no_first_name():
    with pytest.raises(InputError):
        auth_register('bobsmith123@gmail.com', '#abc123', '', 'Smith')

def test_register_long_first_name():
    with pytest.raises(InputError):
        auth_register('bobsmith123@gmail.com', '#abc123', 'a'*51, 'Smith')

def test_register_no_last_name():
    with pytest.raises(InputError):
        auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', '')

def test_register_long_last_name():
    with pytest.raises(InputError):
        auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'a'*51)

def test_register_empty():
    with pytest.raises(InputError):
        auth_register('', '', '', '')
