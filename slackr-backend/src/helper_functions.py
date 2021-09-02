'''
Helper functions to be called accross multiple modules
'''
import os
import os.path
import pickle
import urllib.request
import imghdr
from PIL import Image
from error import AccessError, InputError

DATA_FILE = "datastore.p"

def get_data():
    '''
    Creates a new or loads up previous data storage file upon running
    and returns it
    Parameters:
        None
    Returns:
        data (dicionary of lists): Contains all slackr information
    '''
    if os.path.exists(DATA_FILE) is True and os.path.getsize(DATA_FILE) > 0:
        data = pickle.load(open(DATA_FILE, "rb"))
    else:
        data = {
            'profiles': [],
            'users': [],
            'logged_in': [],
            'channels': [],
            'standups': [],
            'total_messages': 0,
            'img_count': 0
        }
        pickle.dump(data, open(DATA_FILE, "wb"))

    return data

def save_data(data):
    '''
    Pickles current data preserving it.
    Parameters:
        data (dictionary of lists): Current data being used
    Returns:
        No returns
    '''
    pickle.dump(data, open(DATA_FILE, "wb"))

def valid_token(token):
    '''
    Raises an access error if given token is invalid
    Parameters:
        token (string): A unique string authorising a users session
    Returns:
        u_id (int): The unique id of the user with the given token
    '''
    data = get_data()
    # Returns user id if given a valid token for that user
    for user in data['logged_in']:
        if user['token'] == token:
            return user['u_id']

    # Raises an Access Error is given an invalid token
    raise AccessError(description='You must be a valid user to operate this function.')

def get_member_from_u_id(data, u_id):
    '''
    Returns the member dictionary given a u_id
    Parameters:
        data (dictionary of lists): Current database for slackr
        u_id (int): Unique id of a given user
    Returns:
        Member_dict (dictionary): Contains users id, first and last name,
        {'u_id': u_id (int), 'name_first': first (string), 'name_last': last (string)}
    '''
    for user in data['users']:
        if user['u_id'] == u_id:
            member_dict = {'u_id': u_id,
                           'name_first': user['name_first'],
                           'name_last': user['name_last'],
                           'profile_img_url': user['profile_img_url']
                           }
            return member_dict
    raise InputError(description='No user with given u_id exists')

def check_if_slackr_owner(u_id):
    '''
    Finds if user with given ID is a slackr owner.
    Assumes a valid u_id is given, will return False if not
    Parameters:
        u_id (int): The unique integer of a specific user
    Returns:
        is_slackr_owner (bool): Returns whether or not a user is a slackr owner
    '''
    data = get_data()

    for profile in data['profiles']:
        if u_id == profile['u_id']:
            return bool(profile['is_slackr_owner'] == 1)
    return False

def is_in_channel(u_id, channel):
    '''
    Finds if user is in a given channel, given the channel dictionary
    Parameters:
        u_id (int): The unique integer of a specific user
        channel (dictionary): Dictionary containing information of a channel,
        including 'all_members'
    Returns:
        True/False (bool): Returns whether or not a user is in a given channel
    '''
    for member in channel['all_members']:
        if u_id == member['u_id']:
            return True
    return False

def is_channel_owner(u_id, channel):
    '''
    Finds if user is owner in a given channel, given the channel dictionary
    Parameters:
        u_id (int): The unique integer of a specific user
        channel (dictionary): Dictionary containing information of a channel,
        including 'all_members'
    Returns:
        True/False (bool): Returns whether or not a user is an owner of
        a given channel
    '''
    for member in channel['owner_members']:
        if u_id == member['u_id']:
            return True
    return False

def down_crop_save(token, img_url, x_start, y_start, x_end, y_end):
    '''
    Downloads, crops and returns the path of an image
    given size parameters
    '''
    data = get_data()
    u_id = valid_token(token)
    image_count = data['img_count'] + 1
    data['img_count'] += 1
    # Check HTTP Code
    request = urllib.request.urlopen(img_url)
    if request.getcode() != 200:
        raise InputError(description='Image url returns invalid HTTP status.')

    # Download and store in src/static as user_u_id.jpg
    filename = str(image_count) + 'user_' + str(u_id) + '.jpg'
    path = 'src/static/' + filename

    if os.path.exists(path):
        # Remove existing image
        os.remove(path)

    urllib.request.urlretrieve(img_url, path)

    # Check img type
    if imghdr.what(path) != 'jpeg':
        # Delete file
        os.remove(path)
        raise InputError(description='Image type is required to be Jpeg.')

    # Crop
    img = Image.open(path)
    crop_size = (x_start, y_start, x_end, y_end)
    curr_width, curr_height = img.size
    if x_start < 0 or y_start < 0 or x_end > curr_width or y_end > curr_height:
        os.remove(path)
        raise InputError(description='Values are not within image size.')
    img = img.crop(crop_size)

    # Save
    img.save(path)

    img.show()

    path = path[3:]
    return path, filename
