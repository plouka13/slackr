'''
Channel functions located in this module, including:
channel_invite, channel_join, channel_leave, channel_addowner, channel_removeowner,
channel_details, channel_messages
'''
from error import InputError, AccessError
from helper_functions import (get_data,
                              save_data,
                              valid_token,
                              get_member_from_u_id,
                              check_if_slackr_owner,
                              is_in_channel,
                              is_channel_owner)

def channel_invite(token, channel_id, u_id):
    '''
    Invites and adds a user to join a specific channel.
    Parameters:
        token (string): A unique string authorising a users session
        channel_id (int): An integer unique to a specific channel
        u_id (int): An integer unique to a specific user
    Return:
        {} (empty dictionary): No return value
    '''
    data = get_data()
    u_id_inviter = valid_token(token)
    member_dict = get_member_from_u_id(data, u_id)

    # checking channel_id for InputError
    channel = check_valid_channel_id(data, channel_id)

    if not is_in_channel(u_id_inviter, channel):
        raise AccessError(description='authorised user is not already a member of the channel')

    if member_dict not in channel['all_members']:
        channel['all_members'].append(member_dict)

    if check_if_slackr_owner(u_id) is True:
        channel['owner_members'].append(member_dict)

    save_data(data)

    return {}



def channel_join(token, channel_id):
    '''
    Adds authorised user to specific channel
    Parameters:
        token (string): A unique string authorising a users session
        channel_id (int): An integer unique to a specific channel
    Returns:
        {} (empty dictionary): No return value
    '''
    data = get_data()
    u_id = valid_token(token)
    member_dict = get_member_from_u_id(data, u_id)

    channel = check_valid_channel_id(data, channel_id)

    # Finds if user is a slackr owner_members
    is_slackr_owner = check_if_slackr_owner(u_id)

    # private channel and user not (in owner list OR is slackr owner)
    if (
            not channel['is_public'] and not
            (member_dict in channel['owner_members'] or is_slackr_owner)
        ):
        raise AccessError(description='channel is private and user is not admin')

    else:
        # add user as member if not already in channel
        if member_dict not in channel['all_members']:
            channel['all_members'].append(member_dict)

        if is_slackr_owner:
            channel['owner_members'].append(member_dict)
        save_data(data)
    return {}

def channel_leave(token, channel_id):
    '''
    User is removed as a member of the given channel
    Parameters:
        token (string): A unique string authorising a users session
        channel_id (int): An integer unique to a specific channel
    Returns:
        {} (empty dictionary): No return value
    '''
    data = get_data()
    channel = check_valid_channel_id(data, channel_id)
    u_id = valid_token(token)
    member_dict = get_member_from_u_id(data, u_id)

    # Removes user if in channel
    if is_in_channel(u_id, channel) is False:
        raise AccessError(description='user is not a member of channel with channel_id')
    else:
        channel['all_members'].remove(member_dict)

    # Removes previous owner from owner members
    if is_channel_owner(u_id, channel):
        channel['owner_members'].remove(member_dict)

    save_data(data)

    return {}

def channel_addowner(token, channel_id, u_id_to_add):
    '''
    Makes user of u_id_to_add an owner of the channel
    Parameters:
        token (string): A unique string authorising a users session
        channel_id (int): An integer unique to a specific channel
        u_id_to_add (int): A unique integer identifying a different user
    Returns:
        {} (empty dictionary): No return value
    '''
    data = get_data()
    channel = check_valid_channel_id(data, channel_id)
    u_id = valid_token(token)
    member_dict = get_member_from_u_id(data, u_id)
    member_dict_to_add = get_member_from_u_id(data, u_id_to_add)

    #get_user_from_u_id(data, u_id_to_add)

    for owner in channel['owner_members']:
        if owner['u_id'] == u_id_to_add:
            raise InputError(description='user with u_id already owner of channel')

    if not (check_if_slackr_owner(u_id) or (member_dict in channel['owner_members'])):
        raise AccessError(description='authorised user is not an owner of the slackr, \
            or an owner of this channel')

    if not member_dict_to_add in channel['all_members']:
        channel['all_members'].append(member_dict_to_add)

    channel['owner_members'].append(member_dict_to_add)
    save_data(data)
    return {}

def channel_removeowner(token, channel_id, u_id_to_remove):
    '''
    Removes the user of u_id_to_add an owner of the channel
    Parameters:
        token (string): A unique string authorising a users session
        channel_id (int): An integer unique to a specific channel
        u_id_to_remove (int) 
    Returns:
        {} (empty dictionary): No return value
    '''
    data = get_data()
    channel = check_valid_channel_id(data, channel_id)
    u_id = valid_token(token)
    member_dict = get_member_from_u_id(data, u_id)
    member_dict_to_remove = get_member_from_u_id(data, u_id_to_remove)#check valid target u_id

    # checking if u_id_to_remove is an owner
    if member_dict_to_remove not in channel['owner_members']:
        raise InputError(description='user with u_id is not an owner of the channel')

    if not (check_if_slackr_owner(u_id) or (member_dict in channel['owner_members'])):
        raise AccessError(description='authorised user is not an owner of the slackr \
            or an owner of this channel')


    channel['owner_members'].remove(member_dict_to_remove)

    save_data(data)
    return {}

def check_valid_channel_id(data, channel_id):
    '''
    Local function which checks if channel exists, raises InputError otherwise.
    Parameters:
        data (List of dictionaries): Passes in the slackr data information
        channel_id (int): An integer unique to a specific channel
    Returns:
        Channel (dictionary): Contains { channel_id (int), name (string)}
    '''
    for channel in data['channels']:
        if channel_id == channel['channel_id']:
            return channel
    raise InputError(description='channel_id does not refer to a valid channel')



def channel_details(token, channel_id):
    '''
    Provides basic details about the channel
    Parameters:
        token (string): A unique string authorising a users session
        channel_id (int): An integer unique to a specific channel
    Returns:
        Channel (dictionary): Contains {channel_id (int), 
                                        name (string), 
                                        all_members (list)}
    '''
    data = get_data()
    channel = check_valid_channel_id(data, channel_id)
    u_id = valid_token(token)
    member_dict = get_member_from_u_id(data, u_id)
    
    if is_in_channel(u_id, channel) is False:
        raise AccessError(description='user is not a member of channel with channel_id')
    
    for member in channel['all_members']:
        if member['u_id'] == u_id:
            member = member_dict

    for member in channel['owner_members']:
        if member['u_id'] == u_id:
            member = member_dict

    save_data(data)

    return {'name': channel['name'],
            'owner_members': channel['owner_members'],
            'all_members': channel['all_members']}


def channel_messages(token, channel_id, start):
    '''
    Retrieves up to 50 messages in a channel beginning from the start index
    Parameters:
        token (string): A unique string authorising a users session
        channel_id (int): An integer unique to a specific channel
        start (int): Index of the most recent message to collect
    Returns:
        {'messages': returned_messages, 'start': start, 'end': end} (dictionary): 
        Contains { messages (list of dictionaries), start index (int), end index(int)}
    '''
    data = get_data()
    channel = check_valid_channel_id(data, channel_id)
    u_id = valid_token(token)
    member_dict = get_member_from_u_id(data, u_id)

    messages = channel['messages']
    # empty case
    if len(messages) == 0 and start == 0: #pylint: disable=len-as-condition
        return {'messages': [], 'start': start, 'end': -1}

    if start >= len(messages):
        raise InputError(description='start is greater than the total number \
            of messages in the channel')

    if is_in_channel(u_id, channel) is False:
        raise AccessError(description='user is not a member of channel with channel_id')
    
    end = start + 50
    returned_messages = messages[start:end]
    if end >= len(messages):
        end = -1

    return {'messages': returned_messages, 'start': start, 'end': end}
