'''
Message functions are located in this module, including:
message_send, message_sendlater, message_react, message_unreact, message_pin,
message_unpin, message_remove, message_edit
'''
import time
from helper_functions import (
    get_data,
    save_data,
    valid_token,
    check_if_slackr_owner
)
from error import InputError, AccessError

def message_send(token, channel_id, message):
    '''
    Sends a message to a given channel
    parameters:
        token (string): A unique string authorising a users session
        channel_id (int): An integer unique to a specific channel
        message (string): An string less than 1000 characters long
    returns:
        {'message_id': message_id (int)}: The unique id of the sent message
    '''
    data = get_data()
    # Checking token is valid
    u_id = valid_token(token)

    # Check if message too long
    if len(message) > 1000:
        raise InputError(description='Message too long.')

    # Check if channel_id is valid
    if channel_id > len(data['channels']) or channel_id <= 0:
        raise InputError(description='Invalid channel_id.')


    # message_id is created, valued one higher than the previous
    message_id = data['total_messages'] + 1
    data['total_messages'] += 1

    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            for member in channel['all_members']:
                if u_id == member['u_id']:
                    # Add message to data
                    channel['messages'].insert(0, {
                        'message_id': message_id,
                        'u_id': u_id,
                        'message': message,
                        'time_created': int(time.time()),
                        'reacts': [],
                        'is_pinned': False
                    })

                    save_data(data)

                    return {'message_id': message_id}

    raise AccessError(description='User not in the channel.')

def message_sendlater(token, channel_id, message, time_sent):
    '''
    Sends message to channel with channel_id at a later time
    parameters:
        token (string): A unique string authorising a users session
        channel_id (int): An integer unique to a specific channel
        message (string): An string less than 1000 characters long
        time_sent (unix timestamp): A time in future for the message to be sent
    returns:
        {'message_id': message_id (int)}: The unique id of the sent message
    '''
    data = get_data()
    # Checking token is valid
    u_id = valid_token(token)

    # Check if message too long
    if len(message) > 1000:
        raise InputError(description='Message too long.')

    # Check if the time is in the future
    if time.time() - time_sent > 0:
        raise InputError(description='Time sent is a time in the past.')

    # Check if channel_id is valid
    if channel_id > len(data['channels']) or channel_id <= 0:
        raise InputError(description='Invalid channel_id.')

    # message_id is created, valued one higher than the previous
    message_id = data['total_messages'] + 1
    data['total_messages'] += 1

    # If user is in channel add message data
    for channel in data['channels']:
        if channel['channel_id'] == channel_id:
            for member in channel['all_members']:
                if u_id == member['u_id']:
                    # Add message to data
                    channel['messages'].insert(0, {
                        'message_id': message_id,
                        'u_id': u_id,
                        'message': message,
                        'time_created': time_sent,
                        'reacts': [],
                        'is_pinned': False
                    })

                    save_data(data)

                    return {'message_id': message_id}

    # Else raise error
    raise AccessError(description='User not in the channel.')

def message_react(token, message_id, react_id):
    '''
    Given a message_id within a channel user is part of,
    add a "react" to that particular message
    parameters:
        token (string): A unique string authorising a users session
        message_id (int): An integer unique to a specific message
        react_id (int): A number corresponding to an emoticon reaction, 
                        currently only 1 is a valid react id
    returns:
        {} (empty dictionary): No return value
    '''

    data = get_data()

    # Validating token
    u_id = valid_token(token)

    # Validating message_id
    message = check_valid_message_id(data, message_id)

    # Validating react_id
    if 0 < react_id < 1: # potential to add more react_ids
        raise InputError(description='Invalid react_id.')


    if len(message['reacts']) == 0: #pylint: disable=len-as-condition
        # If no reacts, create Data structure
        message['reacts'].append({
            'react_id': react_id,
            'u_ids': [{'u_id': u_id}],
            'is_this_user_reacted': True
        })
    else:
        for react in message['reacts']:
            if react_id == react['react_id']:
                # react with react_id exists
                for person in react['u_ids']:
                    if person['u_id'] == u_id:
                        # User has already reacted
                        raise InputError(description='User has already reacted to this message.')
                # Add user to list u_ids
                react['u_ids'].append({
                    'u_id': u_id
                })
                react['is_this_user_reacted'] = True
            else:
                # new react with react_id
                message['reacts'].append({
                    'react_id': react_id,
                    'u_ids': [{'u_id': u_id}],
                    'is_this_user_reacted': True
                })
    save_data(data)
    return {}

def message_unreact(token, message_id, react_id):
    '''
    Given a message_id within a channel user is part of,
    remove a "react" from message.
    parameters:
        token (string): A unique string authorising a users session
        message_id (int): An integer unique to a specific message
        react_id (int): A number corresponding to an emoticons reaction
    returns:
        {} (empty dictionary): No Returns
    '''

    data = get_data()

    # Validating token
    u_id = valid_token(token)

    # Validating message_id
    message = check_valid_message_id(data, message_id)

    # Validating react_id
    if 0 < react_id < 1: # potential to add more react_ids
        raise InputError(description='Invalid react_id.')

    for react in message['reacts']:
        if react_id == react['react_id']:
            # React exists
            if {'u_id': u_id} not in react['u_ids']:
                # User has not reacted, error
                raise InputError(description='User has not reacted to this message.')
            else:
                # User has reacted, remove
                react['u_ids'].remove({'u_id': u_id})
                react['is_this_user_reacted'] = False
                if len(react['u_ids']) == 0: #pylint: disable=len-as-condition
                    message['reacts'].remove(react)
                save_data(data)
                return {}
        else:
            raise InputError(description='Message does not have react with react_id.')

def message_pin(token, message_id):
    '''
    Given a message within a channel,
    mark it as "pinned"
    parameters:
        token (string): A unique string authorising a users session
        message_id (int): An integer unique to a specific message
    returns:
        {} (empty dictionary): No Returns
    '''

    data = get_data()

    # Validating token
    u_id = valid_token(token)

    # Validating message_id
    message = check_valid_message_id(data, message_id)

    # Get channel_id from message_id
    channel = get_channel_from_message_id(data, message_id)

    # Check is user is owner
    is_owner = check_user_is_owner(data, u_id, channel['channel_id'])

    if not is_owner:
        # User is not owner
        raise InputError(description='User is not an owner of the channel.')

    if message['is_pinned']:
        # Message already pinned
        raise InputError(description='Message is already pinned.')

    for owner in channel['owner_members']:
        if owner['u_id'] == u_id:
            message['is_pinned'] = True
            save_data(data)
            return {}

    # user not part of channel
    raise AccessError(description='User is not part of the channel')

def message_unpin(token, message_id):
    '''
    Given a pinned message within a channel,
    mark it as "unpinned"
    parameters:
        token (string): A unique string authorising a users session
        message_id (int): An integer unique to a specific message
    returns:
        {} (empty dictionary): No Returns
    '''
    data = get_data()

    # Validating token
    u_id = valid_token(token)

    # Validating message_id
    message = check_valid_message_id(data, message_id)

    # Get channel_id from message_id
    channel = get_channel_from_message_id(data, message_id)

    # Check is user is owner
    is_owner = check_user_is_owner(data, u_id, channel['channel_id'])

    if not is_owner:
        # User is not owner
        raise InputError(description='User is not an owner of the channel.')

    if not message['is_pinned']:
        # Message not pinned
        raise InputError(description='Message is not pinned.')

    for owner in channel['owner_members']:
        if owner['u_id'] == u_id:
            message['is_pinned'] = False
            save_data(data)

    return {}

def message_remove(token, message_id):
    '''
    Given a messages id, it's removed from its channel
    parameters:
        token (string): A unique string authorising a users session
        message_id (int): An integer unique to a specific message
    returns:
        {} (empty dictionary): No Returns
    '''
    data = get_data()

    # Validating token
    u_id = valid_token(token)

    # Validating message_id
    message = check_valid_message_id(data, message_id)

    # Get channel_id from message_id
    channel = get_channel_from_message_id(data, message_id)

    if (
            message['u_id'] != u_id and not
            check_user_is_owner(data, u_id, channel['channel_id']) and not
            check_if_slackr_owner(u_id)
        ):
        raise AccessError(description='User is not owner of message, channel or slackr.')

    channel['messages'].remove(message)
    data['total_messages'] -= 1
    save_data(data)
    return {}

def message_edit(token, message_id, new_message):
    '''
    Given a message_id edit its contents and replace with message given
    parameters:
        token (string): A unique string authorising a users session
        message_id (int): An integer unique to a specific message
        new_message (string): A string 1000 or less characters long
    returns:
        {} (empty dictionary): No Returns
    '''
    data = get_data()

    # Validating token
    u_id = valid_token(token)

    # Validating message_id
    message = check_valid_message_id(data, message_id)

    # Get channel_id from message_id
    channel = get_channel_from_message_id(data, message_id)

    if (
            message['u_id'] != u_id and not
            check_user_is_owner(data, u_id, channel['channel_id']) and not
            check_if_slackr_owner(u_id)
        ):
        raise AccessError(description='User is not owner of message, channel or slackr.')

    if new_message == '':
        message_remove(token, message_id)
        return {}

    message['message'] = new_message

    save_data(data)
    return {}
# HELPER FUNCTIONS

def check_valid_message_id(data, message_id): #pylint: disable=inconsistent-return-statements
    '''
    Local function which checks if given message_id is valid, raises error if not
    parameters:
        data (dictionary of lists): Current data in slackr
        message_id (int): An integer unique to a specific message in a
        specific channel
    returns:
        message (string): Returns the message with given id
    '''
    valid_message_id = False
    for channel in data['channels']:
        for message in channel['messages']:
            if message_id == message['message_id']:
                valid_message_id = True
                return message
    if not valid_message_id:
        raise InputError(description="Message doesn't exist.")

def get_channel_from_message_id(data, message_id): #pylint: disable=inconsistent-return-statements
    '''
    Local function which returns channel a given message is in
    parameters:
        data (dictionary of lists): Current data in slackr
        message_id (int): An integer unique to a specific message in a
        specific channel
    returns:
        channel (dictionary): Contains { channel_id (int), name (string)}
    '''
    for channel in data['channels']:
        for message in channel['messages']:
            if message_id == message['message_id']:
                # Message exists
                return channel
    return None

def check_user_is_owner(data, u_id, channel_id):
    '''
    Local function which checks if u_id is an owner
    of the given channel with channel_id
    parameters:
        data (dictionary of lists): Current data in slackr
        u_id (int): An integer unique to a specific user
        channel_id (int): An integer unique to a specific channel
    returns:
        True/False (bool): Returns true if user is an owner of a channel
    '''
    for channel in data['channels']:
        if channel_id == channel['channel_id']:
            for user in channel['owner_members']:
                if u_id == user['u_id']:
                    return True
    return False
