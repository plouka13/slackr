import pytest
from error import InputError, AccessError
from auth import auth_register, auth_logout
from other import admin_userpermission_change
from channels import channels_create
from channel import channel_join, channel_details
from server import reset_req
from helper_functions import get_data

@pytest.fixture(autouse=True)
def reset_state():
    reset_req()

def test_admin_userpermission_change_invalid_token():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    auth_logout(user['token'])

    with pytest.raises(AccessError):
        admin_userpermission_change(user['token'], user['u_id'], 1)

def test_admin_userpermission_change_success():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_register('barbarajones@gmail.com', '#abc123', 'Barbara', 'Jones')

    admin_userpermission_change(user['token'], user2['u_id'], 1)
    data = get_data()
    assert 1 == data['profiles'][1]['is_slackr_owner']  

def test_admin_userpermission_invalid_permission_id():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_register('barbarajones@gmail.com', '#abc123', 'Barbara', 'Jones')

    with pytest.raises(InputError):
        admin_userpermission_change(user['token'], user2['u_id'], 0)

def test_admin_userpermission_atleast_one_slackr_owner():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_register('barbarajones@gmail.com', '#abc123', 'Barbara', 'Jones')

    admin_userpermission_change(user['token'], user2['u_id'], 1)
    admin_userpermission_change(user2['token'], user['u_id'], 2)

    data = get_data()
    
    assert data['profiles'][0]['is_slackr_owner'] == 2
    assert data['profiles'][1]['is_slackr_owner'] == 1

def test_admin_userpermission_only_slackr_owner():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_register('barbarajones@gmail.com', '#abc123', 'Barbara', 'Jones')

    with pytest.raises(AccessError):
        admin_userpermission_change(user['token'], user['u_id'], 2)

def test_admin_userpermission_caller_not_slackr_owner():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_register('barbarajones@gmail.com', '#abc123', 'Barbara', 'Jones')

    with pytest.raises(AccessError):
        admin_userpermission_change(user2['token'], user['u_id'], 2)

def test_admin_userpermission_user2_doesnt_exist():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')

    with pytest.raises(InputError):
        admin_userpermission_change(user['token'], 2, 2)

def test_admin_userpermission_new_owner_channel_priviledges_change():
    user = auth_register('bobsmith123@gmail.com', '#abc123', 'Bob', 'Smith')
    user2 = auth_register('barbarajones@gmail.com', '#abc123', 'Barbara', 'Jones')

    channel_id = channels_create(user['token'], 'channel1', True)['channel_id']
    channel_join(user2['token'], channel_id)

    details = channel_details(user['token'], channel_id)
    assert len(details['owner_members']) == 1

    admin_userpermission_change(user['token'], user2['u_id'], 1)
    
    details = channel_details(user['token'], channel_id)
    assert len(details['owner_members']) == 2
