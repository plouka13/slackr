'''
Flask server and routes contained & run here
'''
import sys
from json import dumps
import hashlib
from flask import Flask, request, url_for, make_response
from flask_cors import CORS
from auth import (
        auth_register,
        auth_login,
        auth_logout,
        passwordreset_request,
        passwordreset_reset
        )
from channels import channels_create, channels_listall, channels_list
from channel import (
        channel_invite,
        channel_join,
        channel_leave,
        channel_addowner,
        channel_removeowner,
        channel_details,
        channel_messages
        )
from message import (
        message_send,
        message_sendlater,
        message_react,
        message_unreact,
        message_pin,
        message_unpin,
        message_remove,
        message_edit
        )
from user import (
        user_profile,
        user_profile_setname,
        user_profile_setemail,
        user_profile_uploadphoto,
        user_profile_sethandle
    )
from other import (
        search,
        admin_userpermission_change,
        admin_user_remove,
        users_all,
        standup_start,
        standup_active,
        standup_send,
    )
from hangman import (
        register_hangman,
        play_round
    )

from helper_functions import save_data, get_data, down_crop_save

def default_handler(err):
    '''
    defaults
    '''
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, default_handler)

@APP.route('/auth/logout', methods=['POST'])
def auth_logout_req():
    '''
    Logs a user out of a session
    Method:
        POST
    Parameters:
        {'token': token (string)}:
        Requires an authorised users token
    Returns:
        {'is_success': True/False (bool)}:
        Returns booleon of whether or not user logged out
    '''

    token = request.get_json()['token']

    return dumps(auth_logout(token))

@APP.route('/auth/login', methods=['POST'])
def auth_login_req():
    '''
    Logs a user in to a new session
    Method:
        POST
    Parameters:
        {'email': email (string),'password': password (string)}
        User logs in using their email and password
    Returns:
        {'token': token (string), 'u_id': u_id (int)}
        Returns an token authorising their session and their u_id
    '''
    email = request.get_json()['email']
    password = hashlib.sha256(request.get_json()['password'].encode()).hexdigest()

    return dumps(auth_login(email, password))

@APP.route('/auth/register', methods=['POST'])
def auth_register_req():
    '''
    Creates a new user in the slackr
    Method:
        POST
    Parameters:
        {'email': email (string),
        'password': password (string),
        'name_first': name_first (string between 1-50 characters),
        'name_last': name_last (string between 1-50 characters)}
    Returns:
        {'token': token (string), 'u_id': u_id (int)}
        Returns an token authorising their session and their u_id
    '''
    email = request.get_json()['email']
    password = hashlib.sha256(request.get_json()['password'].encode()).hexdigest()
    name_first = request.get_json()['name_first']
    name_last = request.get_json()['name_last']

    return dumps(auth_register(email, password, name_first, name_last))

@APP.route('/channels/create', methods=['POST'])
def channels_create_req():
    '''
    Creates a new channel
    Method:
        POST
    Parameters:
        {'token': Token (unique string authorising user session),
         'name': name (name string of new channel between 1-20 characters long),
         'is_public': True/False (bool determining whether channel is public)}
    Returns:
         {'channel_id': channel_id (unique integer given to specific channel)}
    '''
    token = request.get_json()['token']
    name = request.get_json()['name']
    is_public = request.get_json()['is_public']

    return dumps(channels_create(token, name, is_public))

@APP.route('/check', methods=['GET'])
def check_data_req():
    '''
    checks current data
    Method:
        GET
    Parameters:
        None
    Returns:
        data structure
    '''
    data = get_data()
    return data

@APP.route('/channels/list', methods=['GET'])
def channels_list_req():
    '''
    Lists channels that user is a member of
    Method:
        GET
    Parameters:
        Token (unique string authorising user session)}
    Returns:
        {'channels': channels (list)} (dictionary containing list of dictionaries):
        Returns list of channel dictionaries containing
        {'channel_id': channel_id (int), 'name': channel_name (string)}
    '''
    token = request.args.get('token')

    return dumps(channels_list(token))

@APP.route('/channels/listall', methods=['GET'])
def channels_listall_req():
    '''
    Lists all channels on slack
    Method:
        GET
    Parameters:
        Token (unique string authorising user session)}
    Returns:
        {'channels': channels (list)} (dictionary containing list of dictionaries):
        Returns list of channel dictionaries containing
        {'channel_id': channel_id (int), 'name': channel_name (string)}
    '''
    token = request.args.get('token')

    return dumps(channels_listall(token))

@APP.route('/message/send', methods=['POST'])
def message_send_req():
    '''
    Sends a message to a channel
    Method:
        POST
    Parameters:
        {'token': Token (unique string authorising user session),
        'channel_id': channel_id (unique integer assigned to channel),
        'message': message (a string 1-1000 characters long)}
    Returns:
        {'message_id': message_id (unique integer given to sent message)}
    '''
    token = request.get_json()['token']
    channel_id = int(request.get_json()['channel_id'])
    message = request.get_json()['message']

    # check if playing hangman
    if message == "/hangman":
        return dumps(register_hangman(token, channel_id))
    if message[0:7] == "/guess ":
        return dumps(play_round(token, channel_id, message[7:]))

    return dumps(message_send(token, channel_id, message))

@APP.route('/message/sendlater', methods=['POST'])
def message_sendlater_req():
    '''
    Sends a message to a channel at a specified time later in the future
    Method:
        POST
    Parameters:
        {'token': Token (unique string authorising user session),
        'channel_id': channel_id (unique integer assigned to channel),
        'message': message (a string 1-1000 characters long),
        'time_sent': time_sent (unix timestamp of when message should be sent)}
    Returns:
        {'message_id': message_id (unique integer given to sent message)}
    '''
    token = request.get_json()['token']
    channel_id = int(request.get_json()['channel_id'])
    message = request.get_json()['message']
    time_sent = int(request.get_json()['time_sent'])

    return dumps(message_sendlater(token, channel_id, message, time_sent))

@APP.route('/message/react', methods=['POST'])
def message_react_req():
    '''
    Reacts to a message in a channel
    Method:
        POST
    Parameters:
        {'token': Token (unique string authorising user session),
        'message_id': message_id (unique integer assigned to a message),
        'react_id': react_id (an integer corresponding to a specific react,
                              currently can only be 1)}
    Returns:
        {} (empty dictionary): No return value
    '''
    token = request.get_json()['token']
    message_id = int(request.get_json()['message_id'])
    react_id = int(request.get_json()['react_id'])

    return dumps(message_react(token, message_id, react_id))

@APP.route('/message/unreact', methods=['POST'])
def message_unreact_req():
    '''
    Unreacts to a message in a channel
    Method:
        POST
    Parameters:
        {'token': Token (unique string authorising user session),
        'message_id': message_id (unique integer assigned to a message),
        'react_id': react_id (an integer corresponding to a specific react,
                              currently can only be 1)}
    Returns:
        {} (empty dictionary): No return value
    '''
    token = request.get_json()['token']
    message_id = int(request.get_json()['message_id'])
    react_id = int(request.get_json()['react_id'])

    return dumps(message_unreact(token, message_id, react_id))

@APP.route('/message/pin', methods=['POST'])
def message_pin_req():
    '''
    Pins a message
    Method:
        POST
    Parameters:
        {'token': Token (unique string authorising user session),
        'message_id': message_id (unique integer assigned to a message)}
    Returns:
        {} (empty dictionary): No return value
    '''
    token = request.get_json()['token']
    message_id = int(request.get_json()['message_id'])

    return dumps(message_pin(token, message_id))

@APP.route('/message/unpin', methods=['POST'])
def message_unpin_req():
    '''
    Unpins a message
    Method:
        POST
    Parameters:
        {'token': Token (unique string authorising user session),
        'message_id': message_id (unique integer assigned to a message)}
    Returns:
        {} (empty dictionary): No return value
    '''
    token = request.get_json()['token']
    message_id = int(request.get_json()['message_id'])

    return dumps(message_unpin(token, message_id))

@APP.route('/message/remove', methods=['DELETE'])
def message_remove_req():
    '''
    Removes a message from its channel
    Method:
        DELETE
    Parameters:
        {'token': Token (unique string authorising user session),
        'message_id': message_id (unique integer assigned to a message)}
    Returns:
        {} (empty dictionary): No return value
    '''
    token = request.get_json()['token']
    message_id = int(request.get_json()['message_id'])

    return dumps(message_remove(token, message_id))

@APP.route('/message/edit', methods=['PUT'])
def message_edit_req():
    '''
    Edits a message
    Method:
        PUT
    Parameters:
        {'token': Token (unique string authorising user session),
        'message_id': message_id (unique integer assigned to a message)
        'new_message': message (string with length 1-1000 characters)}
    Returns:
        {} (empty dictionary): No return value
    '''
    token = request.get_json()['token']
    message_id = int(request.get_json()['message_id'])
    message = request.get_json()['message']
    return dumps(message_edit(token, message_id, message))

@APP.route('/user/profile', methods=['GET'])
def user_profile_req():
    '''
    Returns the user dictionary of the u_id's corresponding user
    Method:
        GET
    Parameters:
        token (string) unique string authorising user session
        channel_id (int) unique integer assigned to a user
    Returns:
        {'user': {'u_id': users u_id (int),
                   'email': users email (string),
                   'name_first': users first name (string),
                   'name_last': users last name (string),
                   'handle_str': users handle (string),
                   'profile_img_url': url corresponding to their profile picture
                   } (dictionary containing dictionary)
    '''
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))

    return dumps(user_profile(token, u_id))

@APP.route('/user/profile/uploadphoto', methods=['POST'])
def user_profile_uploadphoto_req():
    '''
    Uploads a photo for the user profile
    Method:
        POST
    Parameters:
        {'img_url': img_url (url string),
         'x_start': x_start (integer position),
         'y_start': y_start (integer position),
         'x_end': x_end (integer position),
         'y_end': y_end (integer position)}
    Returns:
        {} (empty dictionary): No return value
    '''
    token = request.get_json()['token']
    img_url = request.get_json()['img_url']
    x_start = int(request.get_json()['x_start'])
    y_start = int(request.get_json()['y_start'])
    x_end = int(request.get_json()['x_end'])
    y_end = int(request.get_json()['y_end'])
    path, filename = down_crop_save(token, img_url, x_start, y_start, x_end, y_end)
    url = url_for("uploaded", path=path, filename=filename)
    print(url)
    return dumps(user_profile_uploadphoto(token, url, PORT))

@APP.route('/<path>', methods=['GET'])
def uploaded(path):
    '''
    Url of uploaded image at path
    '''
    resp = make_response(open(path).read())
    resp.content_type = "image/jpeg"
    resp.show()
    return resp

@APP.route('/user/profile/setname', methods=['PUT'])
def user_profile_setname_req():
    '''
    Changes the first and last name of the calling user
    Method:
        PUT
    Parameters:
        {'token': Token (unique string authorising user session),
        'name_first': name_first (A string between 1 and 20 letters long)
        'name_last': name_last ((A string between 1 and 20 letters long)}
        Both first and last name may only contain letters, apostrophes,
        spaces and hyphens
    Returns:
        {} (empty dictionary): No return value
    '''
    token = request.get_json()['token']
    name_first = request.get_json()['name_first']
    name_last = request.get_json()['name_last']

    user_profile_setname(token, name_first, name_last)
    return {}

@APP.route('/user/profile/setemail', methods=['PUT'])
def user_profile_setemail_req():
    '''
    Changes the email of the calling user
    Method:
        PUT
    Parameters:
        {'token': Token (unique string authorising user session),
        'email': email (A valid, unused email address string)}
    Returns:
        {} (empty dictionary): No return value
    '''
    token = request.get_json()['token']
    email = request.get_json()['email']

    user_profile_setemail(token, email)
    return {}

@APP.route('/user/profile/sethandle', methods=['PUT'])
def user_profile_sethandle_req():
    '''
    Changes the handle of the calling user
    Method:
        PUT
    Parameters:
        {'token': Token (unique string authorising user session),
        'handle_str': handle (A valid, unused handle string 1-20 characters long)}
    Returns:
        {} (empty dictionary): No return value
    '''
    token = request.get_json()['token']
    handle = request.get_json()['handle_str']

    user_profile_sethandle(token, handle)
    return {}

@APP.route('/users/all', methods=['GET'])
def users_all_req():
    '''
    Returns all existing user profiles
    Method:
        GET
    Parameters:
        token (string) unique string authorising user session
    Returns:
        {'users': users (list)} Where each entry of the list is a user dictionary
        containing the following information:
        {'u_id': users u_id (int),
                   'email': users email (string),
                   'name_first': users first name (string),
                   'name_last': users last name (string),
                   'handle_str': users handle (string),
                   'profile_img_url': url corresponding to their profile picture
                   }
    '''
    token = request.args.get('token')

    return dumps(users_all(token))

@APP.route('/search', methods=['GET'])
def search_req():
    '''
    Returns a list of messages which include the given string
    Method:
        GET
    Parameters:
        token (string) unique string authorising user session
        query_str (string)
    Returns:
        {'messages': matches (list)}: Returns a list of the messages
        dictionaries for messages containing the given string
    '''
    token = request.args.get('token')
    query_str = request.args.get('query_str')

    return dumps(search(token, query_str))

@APP.route('/admin/userpermission/change', methods=['POST'])
def admin_underpermission_change_req():
    '''
    Changes the permissions of a given user
    Method:
        POST
    Parameters:
        {'token': Token (unique string authorising user session),
        'u_id': u_id (unique integer of a specific user),
        'permission_id': permission_id (integer either valued 1 (slackr owner)
        or 2 (slackr member)}
    Returns:
        {} (empty dictionary): No return value
    '''
    token = request.get_json()['token']
    u_id = int(request.get_json()['u_id'])
    permission_id = int(request.get_json()['permission_id'])

    admin_userpermission_change(token, u_id, permission_id)
    return {}

@APP.route('/admin/user/', methods=['DELETE'])
def admin_user_remove_req():
    '''
    Given a User by their user ID, remove the user from the slackr.
    Method:
        DELETE
    Parameters:
        {'token': Token (unique string authorising user session),
        'u_id': u_id (unique integer of a specific user)}
    Returns:
        {} (empty dictionary): No return value
    '''
    token = request.get_json()['token']
    u_id = int(request.get_json()['u_id'])

    return dumps(admin_user_remove(token, u_id))

@APP.route('/standup/start', methods=['POST'])
def standup_start_req():
    '''
    Begins a standup in a given server
    Method:
        POST
    Parameters:
        {'token': Token (unique string authorising user session),
        'channel_id': channel_id (unique integer assigned to channel),
        'length': length (integer seconds of how long the standup lasts)}
    Returns:
        {'time_finish': time_finish (integer unix timestamp of when standup ends)}
    '''
    token = request.get_json()['token']
    channel_id = int(request.get_json()['channel_id'])
    length = int(request.get_json()['length'])

    return dumps(standup_start(token, channel_id, length))

@APP.route('/standup/active', methods=['GET'])
def standup_active_req():
    '''
    Checks if there's a standup in a given server
    Method:
        GET
    Parameters:
        token (string) Unique token authorising a users session
        channel_id (integer) Unique integer of a specific channel
    Returns:
        {'is_active': is_active (Booleon value of whether there's an active standup),
         'time_finish': time_finish (Integer unix timestamp of when standup ends)}
    '''
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))

    return dumps(standup_active(token, channel_id))

@APP.route('/standup/send', methods=['POST'])
def standup_send_req():
    '''
    Begins a standup in a given server
    Method:
        POST
    Parameters:
        {'token': Token (unique string authorising user session),
        'channel_id': channel_id (unique integer assigned to channel),
        'message': message (string less than 1000 characters long,
                            including the first name of the calling user)}
    Returns:
        {} (empty dictionary): No return value
    '''
    token = request.get_json()['token']
    channel_id = int(request.get_json()['channel_id'])
    message = request.get_json()['message']

    return dumps(standup_send(token, channel_id, message))

@APP.route('/auth/passwordreset/request', methods=['POST'])
def passwordreset_request_req():
    '''
    Sends an email to a valid user with a unique code to reset their password
    Method:
        POST
    Parameters:
        {'email': email (an email string of a user in the system)}
    Returns:
        {} (empty dictionary): No return value
    '''
    email = request.get_json()['email']

    return dumps(passwordreset_request(email))

@APP.route('/auth/passwordreset/reset', methods=['POST'])
def passwordreset_reset_req():
    '''
    Updates the password of their user if given a valid reset code
    Method:
        POST
    Parameters:
        {'code': code (a random 6 character long string),
         'password': password (string)}
    Returns:
        {} (empty dictionary): No return value
    '''
    code = request.get_json()['reset_code']
    password = hashlib.sha256(request.get_json()['new_password'].encode()).hexdigest()

    return dumps(passwordreset_reset(code, password))

@APP.route('/channel/invite', methods=['POST'])
def channel_invite_req():
    '''
    Invites and adds a user (with user id u_id) to join a channel with ID channel_id.
    Method:
        POST
    Parameters:
        {'token': Token (unique string authorising user session),
        'channel_id': channel_id (unique integer assigned to a channel),
        'u_id': u_id (an integer corresponding to a specific user)}
    Returns:
        {} (empty dictionary): No return value
    '''
    token = request.get_json()['token']
    channel_id = int(request.get_json()['channel_id'])
    u_id = int(request.get_json()['u_id'])

    channel_invite(token, channel_id, u_id)
    return {}

@APP.route('/channel/join', methods=['POST'])
def channel_join_req():
    '''
    Allows a user to try join a given channel
    Method:
        POST
    Parameters:
        {'token': Token (unique string authorising user session),
        'channel_id': channel_id (unique integer assigned to a channel)}
    Returns:
        {} (empty dictionary): No return value
    '''
    token = request.get_json()['token']
    channel_id = int(request.get_json()['channel_id'])

    channel_join(token, channel_id)
    return {}

@APP.route('/channel/leave', methods=['POST'])
def channel_leave_req():
    '''
    Allows a user to try leave a given channel
    Method:
        POST
    Parameters:
        {'token': Token (unique string authorising user session),
        'channel_id': channel_id (unique integer assigned to a channel)}
    Returns:
        {} (empty dictionary): No return value
    '''
    token = request.get_json()['token']
    channel_id = int(request.get_json()['channel_id'])

    channel_leave(token, channel_id)
    return {}

@APP.route('/channel/addowner', methods=['POST'])
def channel_addowner_req():
    '''
    Allows a user to try add an owner to a given channel
    Method:
        POST
    Parameters:
        {'token': Token (unique string authorising user session),
        'channel_id': channel_id (unique integer assigned to a channel),
        'u_id': u_id (an integer corresponding to a specific user)}
    Returns:
        {} (empty dictionary): No return value
    '''
    token = request.get_json()['token']
    channel_id = int(request.get_json()['channel_id'])
    u_id = int(request.get_json()['u_id'])

    channel_addowner(token, channel_id, u_id)
    return {}

@APP.route('/channel/removeowner', methods=['POST'])
def channel_removeowner_req():
    '''
    Allows a user to try remove an owner from a given channel
    Method:
        POST
    Parameters:
        {'token': Token (unique string authorising user session),
        'channel_id': channel_id (unique integer assigned to a channel),
        'u_id': u_id (an integer corresponding to a specific user)}
    Returns:
        {} (empty dictionary): No return value
    '''
    token = request.get_json()['token']
    channel_id = int(request.get_json()['channel_id'])
    u_id = int(request.get_json()['u_id'])

    channel_removeowner(token, channel_id, u_id)
    return {}

@APP.route('/channel/details', methods=['GET'])
def channel_details_req():
    '''
    Returns name, owners and owners of a given channel
    Method:
        GET
    Parameters:
        token (unique string authorising user session)
        channel_id (unique integer assigned to a channel),
    Returns:
        Channel (dictionary): Contains {channel_id (int),
                                        name (string),
                                        all_members (list)}
    '''
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))

    return dumps(channel_details(token, channel_id))

@APP.route('/channel/messages', methods=['GET'])
def channel_messages_req():
    '''
    Returns name, owners and members of a given channel
    Method:
        GET
    Parameters:
        token (unique string authorising user session)
        channel_id (unique integer assigned to a channel)
        start (integer index of the most recent message to collect)
    Returns:
        {'messages': returned_messages, 'start': start, 'end': end} (dictionary):
        Contains { messages (list of dictionaries), start index (int), end index (int)}
    '''
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))

    return dumps(channel_messages(token, channel_id, start))

@APP.route('/workspace/reset', methods=['POST'])
def reset_req():
    '''
    Resets the work space
    Method:
        POST
    Parameters:
        None
    Returns:
        None
    '''
    data = {
        'profiles': [],
        'users': [],
        'logged_in': [],
        'channels': [],
        'standups': [],
        'total_messages': 0,
        'img_count': 0
    }
    save_data(data)
    return {}


if __name__ == "__main__":
    PORT = int(sys.argv[1]) if len(sys.argv) == 2 else 8080
    APP.run(debug=True, port=PORT, threaded=True)
