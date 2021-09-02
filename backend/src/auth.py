'''
Auth functions are located in this file, including:
auth_login, auth_logout, auth_register, passwordreset_request, passwordreset_reset
'''
import re
import smtplib
import random
import string
import jwt
from error import InputError
from helper_functions import get_data, save_data, valid_token

SECRET = "the show the office"
VALID_EMAIL = "^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$" #pylint: disable=anomalous-backslash-in-string

def make_handle(name_first, name_last):
    '''
    A local function used to generate a unique handle for new users
    Paramaters:
        name_first (string): a first name between 1 and 50 letters long
        name_last (string): a last name between 1 and 50 letters long
    Return:
        new_handle_str (string): a string between 1 and 20 letters long
    '''
    data = get_data()

    first = name_first.lower()
    last = name_last.lower()[:19]

    handle_str = first[0] + last
    new_handle_str = handle_str
    count = 0

    unique = False
    while unique is False:
        unique = True

        # Loops through to see if there is a duplicate handle
        for user in data['users']:
            if user['handle_str'] == new_handle_str:
                unique = False
                count += 1
                new_handle_str = handle_str + str(count)

                # Duplicate strings at length over 20 are truncated to accomodate
                # for the number attached
                if len(new_handle_str) > 20:
                    new_handle_str = handle_str[:20-len(str(count))] + str(count)

    return new_handle_str

def auth_login(email, password):
    '''
    Function which logs an existing user in to an active session if given
    valid input for profiles in the database
    Paramaters:
        email (string): A users email is passed in, and turned lowercase
        password (string): An encoded password is passed in to the function
    Return:
        {'token': token, 'u_id': u_id} (dictionary) cont. token(string), u_id(int):
        A valid token and u_id corresponding to the logged in user
    '''
    data = get_data()

    # Checks if email exists
    for profile in data['profiles']:
        if email.lower() in profile['email']:
            # Checks correct password is given for user with that password
            if password == profile['password']:

                u_id = profile['u_id']
                token = jwt.encode({'u_id': u_id}, SECRET, algorithm='HS256').decode('utf-8')

                # Add token and u_id dict to logged_in list
                data['logged_in'].append({'token': token, 'u_id': u_id})

                save_data(data)

                return {'token': token, 'u_id': u_id}

    raise InputError(description='Incorrect email or password')

def auth_logout(token):
    '''
    Function which logs out a user from their authorised session
    Paramaters:
        token (int): A string which authorises the users session
    Return:
        {'is_success': True/False}, (Dictionary), True/False (Bool): Returns
        whether or no the user was successfully logged out of their session
    '''
    data = get_data()

    valid_token(token)

    for user in data['logged_in']:
        if token in user['token']:
            data['logged_in'].remove(user)
            save_data(data)
            return {'is_success': True}

    return {'is_success': False}

def email_taken(email, data):
    '''
    Local function which returns True if a user is already registered
    with given email. False otherwise.
    Paramaters:
        email (string): An email is passed
        data (list of dictionaries): data is given to function to read
    Return:
        True/False (Bool): Returns bool is email is currently in use or not
    '''
    for profile in data['profiles']:
        if email in profile['email']:
            return True
    return False

def auth_register_check_input_error(data, email, password, name_first, name_last):
    '''
    Checks for any input errors when a new user is trying to register
    Paramaters:
        data (list of dictionaries): slackr data is passed in
        email (string): the users email address
        password (string): the users password
        name_first (string): A first name between 1 & 50 letters long
        name_last (string): A last name between 1 & 50 letters long
    Return:
        No returned values
    '''
    # check valid email
    if not re.search(VALID_EMAIL, email):
        raise InputError("Invalid email address")

    # check if email already used
    elif email_taken(email, data):
        raise InputError("Email already registered")

    # password too short
    elif len(password) < 6:
        raise InputError("Password less than 6 characters")

    # name requirements between 1 - 50 characters
    elif len(name_first) < 1 or len(name_first) > 50: #pylint: disable=len-as-condition
        raise InputError("Invalid length of first name")
    elif len(name_last) < 1 or len(name_last) > 50: #pylint: disable=len-as-condition
        raise InputError("Invalid length of last name")
    else:
        return


def auth_register(email, password, name_first, name_last):
    '''
    Registers a new user, creating an account and authorising their session
    Paramaters:
        email (string): The users email
        password (string): An encoded password is passed in
        name_first (string): A first name between 1-50 letters long
        name_last (string): A last name between 1-50 letters long
    Return:
        {'token': token, 'u_id': u_id} (dictionary), token (string), u_id (int):
        Returns a unique token to the user authorising their session, and
        their unique u_id
    '''
    data = get_data()
    email = email.lower()
    auth_register_check_input_error(data, email, password, name_first, name_last)

    # u_id is created, valued one higher than the previous users
    if data['users'] == []:
        u_id = 1
        is_slackr_owner = 1

    else:
        u_id = data['users'][-1]['u_id'] + 1
        is_slackr_owner = 2

    # Profile for logging in is create
    data['profiles'].append({
        'email': email,
        'password': password,
        'u_id': u_id,
        'is_slackr_owner': is_slackr_owner
    })

    # A profile is users is added
    data['users'].append({'u_id': u_id,
                          'email': email,
                          'name_first': name_first,
                          'name_last': name_last,
                          'handle_str': make_handle(name_first, name_last),
                          'profile_img_url': ''
                         })

    token = jwt.encode({'u_id': u_id}, SECRET, algorithm='HS256')

    # Add token and u_id dict to logged_in list
    data['logged_in'].append({'token': token,
                              'u_id': u_id
                             })

    save_data(data)

    return {'token': token, 'u_id': u_id}

def passwordreset_request(email):
    '''
    Recieves an email as input
    If email appears in the profile database, they will be emailled a code
    which may be used to let them change their password
    Paramaters:
        email (string): An email address
    Returns:
        {} (empty dictionary): No value is returned
    '''
    data = get_data()
    for profile in data['profiles']:
        if email == profile['email']:

            # Creates a sufficiently random code
            random.seed()
            numbers = str(random.randint(100, 999))
            letters = ''.join(random.choice(string.ascii_letters) for _ in range(0, 3))
            code = numbers + letters

            # Attaches code to the users profile
            profile['reset_code'] = code

            # Creates and formats the email message
            subject = 'Slackr Forgotten Email'
            content = """Hello, It seems you've forgotten your Slackr email!
            Here is your code to reset it: """ + code

            message = f'Subject: {subject}\n\n{content}'

            # Sends email
            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:

                smtp.ehlo()
                smtp.starttls()
                smtp.login('zaintigerslackr@gmail.com', 'dundermifflin')
                smtp.sendmail('zaintigerslackr@gmail.com', email, message)
                smtp.close()

            save_data(data)
            return {}

    raise InputError(description='Email is not registered.')

def passwordreset_reset(code, password):
    '''
    If given a valid reset code for a certain user, that
    users password will be updated to the new password
    Parameters:
        code (string): A random code containing 3 numbers and 3 letters
        password (string): A new password for the user is passed in
    Returns:
        {} (empty dictionary): No return value
    '''
    data = get_data()

    # Checks if the given reset code appears in any of the profiles
    for profile in data['profiles']:
        if 'reset_code' in profile and profile['reset_code'] == code:

            # Removes reset code from profile
            del profile['reset_code']

            # Changes password to new password
            profile['password'] = password

            save_data(data)
            return {}

    raise InputError(description='Reset code not valid.')
