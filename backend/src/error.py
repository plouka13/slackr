'''
Provided error classes
'''
from werkzeug.exceptions import HTTPException

class AccessError(HTTPException):
    '''
    Given AccessError class, which raises a 400 code
    '''
    code = 400
    message = 'No message specified'

class InputError(HTTPException):
    '''
    Given Input Error Class, which raises a 400 code
    '''
    code = 400
    message = 'No message specified'
