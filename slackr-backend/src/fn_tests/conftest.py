import pytest
from auth import auth_register
from server import reset_req

@pytest.fixture (autouse=True)
def reset_state():
    reset_req()

@pytest.fixture
def register_one():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    return user['u_id'], user['token']

@pytest.fixture
def register_two():
    user1 = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_register('brucejones@aol.com', 'xyz789!', 'Bruce', 'Jones')
    return user1, user2

@pytest.fixture
def register_three():
    user1 = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_register('brucejones@aol.com', 'xyz789!', 'Bruce', 'Jones')
    user3 = auth_register('marywilliams@gmail.com', 'p@ssw0rd', 'Mary', 'Williams')

    return [user1, user2, user3]