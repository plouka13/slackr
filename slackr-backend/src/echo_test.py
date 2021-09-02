'''
Provided echo tests
'''
import json
import urllib.request
from urllib.error import HTTPError
import pytest

def test_echo_success():
    '''
    Tests if server works
    '''
    response = urllib.request.urlopen('http://127.0.0.1:8080/echo?data=hi')
    payload = json.load(response)
    assert payload['data'] == 'hi'

def test_echo_failure():
    '''
    Tests if server fails
    '''
    with pytest.raises(HTTPError):
        urllib.request.urlopen('http://127.0.0.1:8080/echo?data=echo')
