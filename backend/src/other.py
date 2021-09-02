'''
Other.py
Contains misc. functions including search, admin_userpermission_change,
standup functions, and pass reset functions
'''
import threading
import time
from error import InputError, AccessError
from helper_functions import (get_data,
                              save_data,
                              valid_token,
                              check_if_slackr_owner,
                              is_in_channel,
                              get_member_from_u_id)

def search(token, string):
    '''
    Finds messages which contain the given string among all channels they
    have access to.
    Parameters:
        token (string): A unique string authorising a users session
        string (string): A substring to be searched for
    Return:
        {'messages': matches (list)}: Returns a list of the messages
        dictionaries for messages containing the given string
    '''

    data = get_data()

    # Checking token is valid
    u_id = valid_token(token)

    # Searches for channels member is apart of
    matches = []
    for channel in data['channels']:
        for member in channel['all_members']:
            if u_id == member['u_id']:

                # Checks messages, ordered from most recent
                for message in channel['messages']:

                    # Appends message information into matched list
                    if string.lower() in message['message'].lower():
                        matches.append(message)

    return {'messages': matches}

def admin_change_error_cases(u_id_caller, u_id_target, permission_id, data):
    '''
    Tests for scenarios which cause an error in admin_change function
    Parameters:
        u_id_caller (int): The u_id of the user calling the admin_change
        u_id_target (int): The u_id of the user getting their permission changed
        permission_id (int): Either valued 1 (slackr owner) or 2 (slackr member)
        data (dictionary): Contains the slackrs current data
    Returns:
        Nothing
    '''
    # Makes sure the caller is themselves an owner
    if check_if_slackr_owner(u_id_caller) is False:
        raise AccessError(description='Authorised user must be an owner.')

    # Makes sure valid permission_id was given
    if permission_id not in [1, 2]:
        raise InputError(description='Permission ID not valid.')

    # Makes sure u_id_target is of an existing user_profile
    if u_id_target not  in range(1, len(data['profiles']) + 1):
        raise InputError(description='User ID must refer to valid user.')

    # If caller is removing their owner status
    if u_id_caller == u_id_target and permission_id == 2:

        # Checks if theres atleast one other owner
        owners = 0
        for user in data['profiles']:
            if check_if_slackr_owner(user['u_id']) is True:
                owners += 1

        # If caller is only owner, they cannot perform this function
        if owners == 1:
            raise AccessError(description='There must be atleast 1 slackr owner.')

def admin_userpermission_change(token, u_id_target, permission_id):
    '''
    Function changes if a user is a slackr admin or not.
    Must be called by someone who is already an admin.
    Parameters:
        token (string): A unique string authorising a users session
        u_id_target (int): The u_id of the user getting their permission changed
        permission_id (int): Either valued 1 (slackr owner) or 2 (slackr member)
    Returns:
        {} (empty dictionary): No return value
    '''
    u_id_caller = valid_token(token)

    data = get_data()

    admin_change_error_cases(u_id_caller, u_id_target, permission_id, data)

    # Changes the permission of the target user
    for user in data['profiles']:
        if user['u_id'] == u_id_target:
            user['is_slackr_owner'] = permission_id

    # A new owner becomes an owner for all channels they are in
    if permission_id == 1:
        for channel in data['channels']:
            if is_in_channel(u_id_target, channel) is True:
                if u_id_target not in channel['owner_members']:
                    user = get_member_from_u_id(data, u_id_target)
                    channel['owner_members'].append({'u_id': user['u_id'],
                                                     'name_first': user['name_first'],
                                                     'name_last': user['name_last']})

    save_data(data)

    return {}

def admin_user_remove(token, u_id_target): #pylint: disable=too-many-branches
# Excess branches come from finding user profile
    '''
    Given a User by their user ID, remove the user from the slackr.
    Parameters:
        token (string): A unique string authorising a users session
        u_id_target (int): The u_id of the user getting their user removed
    Returns:
        {} (empty dictionary): No return value
    '''
    u_id_caller = valid_token(token)

    data = get_data()

    if u_id_caller == u_id_target:
        raise InputError(description='You cannot remove yourself from Slackr.')

    # Checks is caller is an owner
    if check_if_slackr_owner(u_id_caller) is False:
        raise AccessError(description='You must be an owner to remove another user.')

    # Remove profile from profiles
    for user in data['logged_in']:
        if user['u_id'] == u_id_target:
            data['logged_in'].remove(user)

    # Change user data to empty values from users
    for user in data['users']:
        if user['u_id'] == u_id_target:
            user['email'] = ''
            user['handle_str'] = 'rm'
            user['name_first'] = ''
            user['name_last'] = 'REMOVED USER'

    # Remove profile from profiles
    for profile in data['profiles']:
        if profile['u_id'] == u_id_target:
            data['profiles'].remove(profile)
            break
        elif profile not in data['profiles']:
            raise InputError(description='User ID must refer to valid user.')

    # Remove user from all channels they are a part of
    for channel in data['channels']:
        if is_in_channel(u_id_target, channel) is True:
            # in channel
            if u_id_target in channel['owner_members']:
                # owner
                for member in channel['owner_members']:
                    if member['u_id'] == u_id_target:
                        channel['owner_members'].remove(member)
            for member in channel['all_members']:
                # remove from all_members
                if member['u_id'] == u_id_target:
                    channel['all_members'].remove(member)

    save_data(data)

    return {}

def users_all(token):
    '''
    returns a dictionar containing all users
    Parameters:
        token (string): A unique string authorising a users session
    Returns:
        {'users': users (list)} (dictionary containing list):
        List contains user profile dictionaries with the following information
                   {'u_id': users u_id (int),
                   'email': users email (string),
                   'name_first': users first name (string),
                   'name_last': users last name (string),
                   'handle_str': users handle (string),
                   'profile_img_url': url corresponding to their profile picture
                   }
    '''
    valid_token(token)
    data = get_data()
    return {'users': data['users']}

def standup_active(token, channel_id):
    '''
   Checks if theres a standup occuring in a given channel
   Parameters:
        token (string): A unique string authorising a users session
        channel_id (int): An integer unique to a specific channel
    Returns:
        {'is_active': is_active, 'time_finish': time_finish} (dictionary):
        where is_active (bool) and time_finish (unix timestamp)
    '''
    u_id = valid_token(token)
    data = get_data()

    # Checks if channel exists and user is apart of it
    channel_exists = False
    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            for member in channel['all_members']:
                if member['u_id'] == u_id:
                    channel_exists = True
                    break

    if channel_exists is False:
        raise InputError(description='Channel does not exist.')

    # If not found, is_active is false and returns time of finish as None
    is_active = False
    time_finish = None
    for channel in data['standups']:
        if channel['channel_id'] == channel_id:

            # Returns that the channel is active, and time of finish if found
            is_active = True
            time_finish = channel['time_finish']
            break

    return {'is_active': is_active, 'time_finish': time_finish}

def standup_end(channel_id, u_id, length, time_finish):
    '''
    Concludes a standup in a given channel
    Sends formatted message to channel by the user who called the standup
    Parameters:
        channel_id (int): An integer unique to a specific channel
        u_id (int): An integer unique to a specific user
        length (int): Length in seconds of the given standup
        time_finish (unix timestamp): Time when standup concludes
    Returns:
        No return value
    '''
    # Program is buffered for length amount of time before beginning
    time.sleep(length)

    data = get_data()

    message = ""
    for standup in data['standups']:
        if channel_id == standup['channel_id']:
            # Takes message from the standup
            # Removes final newline character from message
            message = standup['messages'][:-1]

            # Removes the standup from standups
            data['standups'].remove(standup)
            save_data(data)

    # Sends nothing if no message was delivered
    if message == "":
        save_data(data)
        return

    # Sends the message as the person who initiated the standup
    for channel in data['channels']:
        if channel['channel_id'] == channel_id:

            if channel['messages'] == []:
                message_id = 1
            else:
                message_id = channel['messages'][-1]['message_id'] + 1

            # Add message to data
            channel['messages'].append({
                'message_id': message_id,
                'u_id': u_id,
                'message': message,
                'time_created': time_finish,
                'reacts': [],
                'is_pinned': False})

            save_data(data)

    return

def standup_start(token, channel_id, length):
    '''
    Begins a standup in a given channel
    Parameters:
        token (string): A unique string authorising a users session
        channel_id (int): An integer unique to a specific channel
        length (int): Length in seconds of the given standup
    Returns:
        {'time_finish': finish (unix timestamp} (dictionary): Contains
        conclusion time of given standup
    '''
    u_id = valid_token(token)
    data = get_data()

    # Checks if user is in the given channel
    for channel in data['channels']:
        if is_in_channel(u_id, channel) is False:
            raise InputError(description='Authorised user must be a member of the given channel.')

    # Checks if a valid length is given
    if length <= 0:
        raise InputError(description='Standup must proceed for atleast 1 second.')

    # Checks if a standup has already commenced
    if standup_active(token, channel_id)['is_active'] is True:
        raise InputError(description='Standup already occuring in channel.')

    # Finishes time of finish by adding length of standup to current time
    finish = int(time.time()) + length

    data['standups'].append({'channel_id': channel_id,
                             'time_finish': finish,
                             'messages': ""})

    save_data(data)

    # Begins thread where the standup waits, takes given messages and posts them
    standup_threat = threading.Thread(target=standup_end, args=(channel_id, u_id, length, finish))
    standup_threat.start()

    return {'time_finish': finish}

def standup_send(token, channel_id, message):
    '''
    Adds a message to a stand ups message queue from a given user
    Parameters:
        token (string): A unique string authorising a users session
        channel_id (int): An integer unique to a specific channel
        message (string): A message less than 1000 characters long,
        including the users first name appended at the front of the message
    Returns:
        {} (empty dictionary): No return value
    '''
    u_id = valid_token(token)
    data = get_data()
    user = get_member_from_u_id(data, u_id)

    # Checks if user is in the given channel
    for channel in data['channels']:
        if is_in_channel(u_id, channel) is False:
            raise InputError(description='Authorised user must be a member of the given channel.')

    # Checks if there's a standup in the given channel
    if standup_active(token, channel_id)['is_active'] is False:
        raise InputError(description='Active Standup is not running in channel.')

    # Creates the message string is desired format
    name = user['name_first']
    message = str.strip(message)
    message = name + ': ' + message + '\n'

    # Ensures each users entire message is less than 1000 characters long
    # excluding the newline character
    if len(message) > 1001:
        raise InputError(description='Message length exceeds 1000 characters.')

    # Appends the string to the rest of the message strings
    for standup in data['standups']:
        if channel_id == standup['channel_id']:
            standup['messages'] = standup['messages'] + message
            save_data(data)

    return {}
