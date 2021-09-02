import pytest
from error import InputError, AccessError
import time
from auth import auth_register, auth_logout
from other import standup_start, standup_send
from channels import channels_create
from channel import channel_messages, channel_join
from helper_functions import get_data
from server import reset_req

LENGTH = 1

@pytest.fixture(autouse=True)
def reset_state():
    reset_req()

def test_standup_send_invalid_token():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']
    standup_start(user['token'], channel_id, LENGTH)
    auth_logout(user['token'])

    with pytest.raises(AccessError):
        standup_send(user['token'], channel_id, "Did no work :p")

def test_standup_send_one_message():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']
    standup_start(user['token'], channel_id, LENGTH)

    standup_send(user['token'], channel_id, "Did no work :p")
    time.sleep(LENGTH)

    channel = get_data()['channels'][0]
    assert channel['messages'][0]['message'] == "Bob: Did no work :p"

def test_standup_send_multiple_messages():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_register('barbarajones@gmail.com', '#abc123', 'Barbara', 'Jones')
    
    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']
    channel_join(user2['token'], channel_id)
    standup_start(user['token'], channel_id, LENGTH)

    standup_send(user['token'], channel_id, "Did no work :p")
    standup_send(user2['token'], channel_id, "Did some work :p")
    time.sleep(LENGTH)

    channel = get_data()['channels'][0]
    assert channel['messages'][0]['message'] == "Bob: Did no work :p\nBarbara: Did some work :p"

def test_standup_send_no_startup():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']

    with pytest.raises(InputError):
        standup_send(user['token'], channel_id, "Did no work :p")

def test_standup_send_invalid_channel_id():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    with pytest.raises(InputError):
        standup_send(user['token'], -1, "Did no work :p")

def test_standup_send_not_channel_member():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_register('barbarajones@gmail.com', '#abc123', 'Barbara', 'Jones')

    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']
    standup_start(user['token'], channel_id, LENGTH)

    with pytest.raises(InputError):
        standup_send(user2['token'], channel_id, "Did no work :p")

def test_standup_send_invalid_length():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']
    standup_start(user['token'], channel_id, LENGTH)

    with pytest.raises(InputError):
        # Msg is 5 characters, + 6 from "Bob: " string appended to front
        # Makes 1001 letter long message in total
        standup_send(user['token'], channel_id, "x"*996)
