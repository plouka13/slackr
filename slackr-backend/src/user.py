'''
Module containing user functions
'''
import re
from error import InputError
from helper_functions import get_data, save_data, valid_token

VALID_EMAIL = r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"

def user_profile(token, u_id):
    '''
    Gets profile information on a user given their u_id
    Parameters:
        token (string): A unique string authorising a users session
        u_id (int): An integer unique to a specific user
    Returns:
        {'user': {'u_id': users u_id (int),
                   'email': users email (string),
                   'name_first': users first name (string),
                   'name_last': users last name (string),
                   'handle_str': users handle (string),
                   'profile_img_url': url corresponding to their profile picture
                   } (dictionary containing dictionary)
    '''
    data = get_data()

    valid_token(token)

    # Returns user dictionary with correct u_id
    for user in data['users']:
        if user['u_id'] == u_id:
            return {'user': user}

    # Raises error if that user doesn't exist
    raise InputError(description='User does not exist')

def user_profile_setname(token, first, last):
    '''
    Changes a users first and last name to given input
    Parameters:
        token (string): A unique string authorising a users session
        first (string): A first name between 1 and 20 letters long
        last (string): A last name between 1 and 20 letters long
        Both first and last name may only contain letters, apostrophes,
        spaces and hyphens
    Returns:
        {} (empty dictionary): No return value
    '''
    data = get_data()

    u_id = valid_token(token)

    # Leading or trailing spaces are removed from the name
    first = str.strip(first)
    last = str.strip(last)

    # Length of names are checked
    if len(first) not in range(1, 51):
        raise InputError(description='First name must be 1-50 characters long.')

    if len(last) not in range(1, 51):
        raise InputError(description='Last name must be 1-50 characters long.')

    # Checks that names contain only letters and select special characters
    acceptable_characters = ["\'", " ", "-"]
    for character in first + last:
        if character.isalpha() is False and character not in acceptable_characters:
            raise InputError(description='Name contains illegal characters!')

    # Changes user names
    for user in data['users']:
        if user['u_id'] == u_id:
            user['name_first'] = first
            user['name_last'] = last
            save_data(data)
    return {}

def user_profile_setemail(token, email):
    '''
    Changes a users profiles email
    Parameters:
        token (string): A unique string authorising a users session
        email (string): A valid email which can't be used by another user
    Returns:
        {} (empty dictionary): No return value
    '''
    data = get_data()
    u_id = valid_token(token)

    # Checks if given string is a valid email
    if not re.search(VALID_EMAIL, email):
        raise InputError(description='Not a valid email.')

    # emails aren't case sensitive but python is, ensures X == x is true
    email = email.lower()

    # Checks if email exists
    for profile in data['profiles']:
        if email in profile['email']:
            raise InputError(description='Email already in use.')

    # Assigns email to the correct user
    for user in data['users']:
        if user['u_id'] == u_id:
            user['email'] = email
            save_data(data)

    for profile in data['profiles']:
        if profile['u_id'] == u_id:
            profile['email'] = email
            save_data(data)
    return {}

def user_profile_uploadphoto(token, url, port):
    '''
    Puts url of image in data structure
    Parameters:
        token (string): A unique string authorising a users session
        url (string): url to the image
        port (integer): 4 digit port number of server
    Returns:
        {} (empty dictionary): No return value
    '''
    data = get_data()
    u_id = valid_token(token)

    url = f'http://127.0.0.1:{port}' + url

    for user in data['users']:
        if user['u_id'] == u_id:
            user['profile_img_url'] = url
            save_data(data)

    for profile in data['profiles']:
        if profile['u_id'] == u_id:
            profile['profile_img_url'] = url
            save_data(data)

    return {}

def user_profile_sethandle(token, handle):
    '''
    Changes a users handle string
    Parameters:
        token (string): A unique string authorising a users session
        handle (string): A 1-20 character long string which must be unique
        to the user, and may contain any characters
    Returns:
        {} (empty dictionary): No return value
    '''
    data = get_data()

    u_id = valid_token(token)

    # Removes any leading or trailing whitespace
    handle = str.strip(handle)

    # Checks in handle in the right length
    if len(handle) not in range(2, 21):
        raise InputError(description='Handle must be between 2-20 characters long.')

    # Checks if handle exists, not case sensitive
    for profile in data['users']:
        if handle.lower() == profile['handle_str'].lower():
            raise InputError(description='Handle already in use.')

    # Changes handle of the correct user
    for user in data['users']:
        if user['u_id'] == u_id:
            user['handle_str'] = handle
            save_data(data)
    return {}
