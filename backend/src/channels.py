'''
Channels functions are located in this module, including:
channels_list, channels_create, channels_listall
'''
from helper_functions import get_data, save_data, valid_token, get_member_from_u_id
from error import InputError

SECRET = "the show the office"

def channels_list(token):
    '''
    Lists all channels that user is a member of
    Parameters:
        token (string): A unique string authorising a users session
    Return:
        {'channels': channels (list)} (dictionary containing list of dictionaries):
        Returns list of channel dictionaries containing
        {'channel_id': channel_id (int), 'name': name (string)}
    '''
    data = get_data()

    # Checking token is valid
    u_id = valid_token(token)

    # Adding membered channel to channels list
    channels = []
    for channel in data['channels']:
        for member in channel['all_members']:
            if u_id == member['u_id']:
                channels.append({
                    'channel_id': channel['channel_id'],
                    'name': channel['name']
                })

    return {'channels': channels}

def channels_listall(token):
    '''
    Lists all channels on slackr
    Parameters:
        token (string): A unique string authorising a users session
    Return:
        {'channels': channels (list)} (dictionary containing list of dictionaries):
        Returns list of channel dictionaries containing
        {'channel_id': channel_id (int), 'name': name (string)}
    '''
    data = get_data()
    # Checking token
    valid_token(token)

    # Adding all channels to channels list
    channels = []
    for channel in data['channels']:
        channels.append({
            'channel_id': channel['channel_id'],
            'name': channel['name']})

    return {'channels': channels}

def channels_create(token, name, is_public):
    '''
    Creates channel with name and whether or not is_public
    Parameters:
        token (string): A unique string authorising a users session
        name (string): the name of a given channel
        is_public (bool): Whether or not anyone can join a given channel
    Return:
        {'channel_id': channel_id (int)} (dictionary): Contains id of new channel
    '''
    data = get_data()

    # Checking token
    u_id = valid_token(token)
    member_dict = get_member_from_u_id(data, u_id)

    # Check if name too long
    if len(name) > 20:
        raise InputError(description='Channel name too long.')

    # channel_id is created, valued one higher than the previous channel
    if data['channels'] == []:
        channel_id = 1
    else:
        channel_id = data['channels'][-1]['channel_id'] + 1

    # Create isPublic and member list
    data['channels'].append({
        'channel_id': channel_id,
        'name': name,
        'is_public': is_public,
        'owner_members': [],
        'all_members': [],
        'messages': [],
        'hangman': None
    })

    # Add u_id to list
    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            channel['all_members'].append(member_dict)
            channel['owner_members'].append(member_dict)

    save_data(data)

    return {'channel_id': channel_id}
