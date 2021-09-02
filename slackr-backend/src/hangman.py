'''
Contains Hangman backend functionality
'''
import random
import string
from error import InputError
from auth import auth_register, auth_login
from channel import check_valid_channel_id
from message import message_send
from helper_functions import (get_data,
                              valid_token,
                              get_member_from_u_id,
                              save_data
                              )

def register_hangman(token, channel_id):
    '''
    Creates a Hangman Bot and adds it to the specified channel.
    Generates a 'hangman' dictionary for the channel that contains the game's secret word
    Parameters:
        token (string): A unique string authorising a users session
        channel_id (int): A unique integer for a specific channel
    Return:
        {'message_id': message_id (int)} (dictionary): Returns message id for the
        hangmans specific message
    '''
    valid_token(token)
    # registering/logging in bot
    hangman_bot = None
    try:
        hangman_bot = auth_login("hangman_bot@slackr.com", "hangman_bot")
    except InputError:
        hangman_bot = auth_register("hangman_bot@slackr.com", "hangman_bot", "Hangman", "Bot")
    data = get_data()

    # adding bot to channel
    hangman_dict = get_member_from_u_id(data, hangman_bot['u_id'])
    channel = check_valid_channel_id(data, channel_id)
    channel['owner_members'].append(hangman_dict)
    channel['all_members'].append(hangman_dict)

    # creating instance of hangman game for the channel
    hangman = create_hangman()
    channel['hangman'] = hangman
    hangman_string = display_game(hangman)
    save_data(data)
    return message_send(hangman_bot['token'], channel_id, hangman_string)


def create_hangman():
    '''
    Creates a hangman object.
    Secret word randomly selected from usr/share/dict/words.
    parameters:
        None
    returns:
        {
        'secret_word': secret_word,
        'lives': 6,
        'guess_so_far': ['_'] * len(secret_word),
        'guessed_letters': [],
        'has_won': False,
        'message': "Guess a letter by typing /guess LETTER"
    } (dictionary): Returns dictionary containing information needed for
    hangman game.
    '''
    wordlist = [line.strip() for line in open('/usr/share/dict/words')]
    secret_word = random.choice(wordlist)
    secret_word = list(secret_word.upper())
    hangman = {
        'secret_word': secret_word,
        'lives': 6,
        'guess_so_far': ['_'] * len(secret_word),
        'guessed_letters': [],
        'has_won': False,
        'message': "Guess a letter by typing /guess LETTER"
    }
    return hangman

def play_round(token, channel_id, guess):
    '''
    Called when user types "/guess LETTER"
    Logs in bot and checks the guess. Sends message to display the game.
    Parameters:
        token (string): A unique string authorising a users session
        channel_id (int): An integer unique to a specific channel
        guess (string): A single letter
    Return:
        {'message_id': message_id (int)} (dictionary): Returns message id for the
        hangman bot message
    '''
    valid_token(token)
    hangman_bot = auth_login("hangman_bot@slackr.com", "hangman_bot")
    data = get_data()
    channel = check_valid_channel_id(data, channel_id)
    hangman = channel['hangman']
    check_guess(hangman, guess)
    hangman_string = display_game(hangman)

    save_data(data)
    return message_send(hangman_bot['token'], channel_id, hangman_string)


def is_valid_guess_input(hangman, guess):
    '''
    Checks if the guess (remainder of string after "/guess ") is valid
    Only accepts a single lower or uppercase letter of the alphabet
    that has not already been guessed
    parameters:
        hangman (dictionary): A dictionary containing details of a specific
        hangman game.
        guess (string): A single letter string
    return:
        valid (bool): Returns whether guess was correct or not
    '''
    guess = guess.upper()

    valid = True
    # not a letter
    if guess not in list(string.ascii_uppercase):
        hangman['message'] = HANGMAN_MESSAGES['invalid']
        valid = False
    # already guessed
    elif guess in hangman['guessed_letters']:
        hangman['message'] = HANGMAN_MESSAGES['repeat']
        valid = False
    return valid

def check_guess(hangman, guess):
    '''
    Handles internal game functionality for hangman.
    Handles gameplay if guess is valid. Updates the hangman message.
    parameters:
        hangman (dictionary): A dictionary containing details of a specific
        hangman game.
        guess (string): A single letter string
    return:
        No returns
    '''
    guess = guess.upper()
    valid = is_valid_guess_input(hangman, guess)
    # valid guess
    if valid:
        # good guess: True if letter in secret word
        good_guess = False
        for idx, letter in enumerate(hangman['secret_word']):
            # good guess, so adding letter to guessed string
            if letter == guess:
                hangman['guess_so_far'][idx] = letter
                good_guess = True
        # guessed letter not in secret_word
        if not good_guess:
            hangman['lives'] = max(hangman['lives'] - 1, 0)

        # add guessed letter to list
        hangman['guessed_letters'].append(guess)
        hangman['message'] = HANGMAN_MESSAGES['guess']
        # check if won
        if hangman['guess_so_far'] == hangman['secret_word']:
            hangman['has_won'] = True
            hangman['message'] = HANGMAN_MESSAGES['won']

        if hangman['lives'] == 0:
            hangman['message'] = HANGMAN_MESSAGES['lost'] + ''.join(hangman['secret_word'])


def display_game(hangman):
    '''
    Displays the hang man game.
    Parameters:
        hangman (dictionary): Dictionary containing information on specific
        hangman game
    Returns:
        hangman_game (ASCII): the string representation of the game
    '''
    # Displaying remaining letters to guess
    remaining_letters = 'Remaining Letters: \n'
    i = 1
    for letter in string.ascii_uppercase:
        if letter in hangman['guessed_letters']:
            remaining_letters += '_'
        else:
            remaining_letters += letter
        if i % 9 == 0:
            remaining_letters += "\n"
        else:
            remaining_letters += ' '
        i += 1
    # ASCII hangman
    hangman_game = HANGMANPICS[hangman['lives']]
    hangman_game += "\n \n"
    # Guessed word
    hangman_game += " ".join(hangman['guess_so_far'])
    # Remaining letters
    hangman_game += "\n \n" + remaining_letters + "\n \n "

    hangman_game += hangman['message']

    return hangman_game



HANGMAN_MESSAGES = {'won': "Congratulations! You won",
                    'lost': "Game over :( \n The secret word was ",
                    'guess': "Guess a letter", 'invalid': "Not a valid letter, try again",
                    'repeat': "Letter already guessed, try again"
                    }

HANGMANPICS = dict([(6, '''
+---+
| \u00A0 \u00A0 |
|
|
|
|
========='''), (5, '''
+---+
| \u00A0 \u00A0 \u00A0 |
| \u00A0 \u00A0 \u00A0 O
|
|
|
========='''), (4, '''
+---+
| \u00A0 \u00A0 \u00A0 |
| \u00A0 \u00A0 \u00A0 O
| \u00A0 \u00A0 \u00A0 |
|
|
========='''), (3, '''
+---+
| \u00A0 \u00A0 \u00A0 |
| \u00A0 \u00A0 \u00A0 O
| \u00A0 \u00A0 \u00A0 /|
|
|
========='''), (2, '''
+---+
| \u00A0 \u00A0 \u00A0  |
| \u00A0 \u00A0 \u00A0  O
| \u00A0 \u00A0 \u00A0 /|\\
|
|
========='''), (1, '''
+---+
|   |
| \u00A0 \u00A0 \u00A0  O
| \u00A0 \u00A0 \u00A0 /|\\ 
| \u00A0 \u00A0 \u00A0/ 
|
========='''), (0, '''
+---+
| \u00A0 \u00A0 \u00A0  |
| \u00A0 \u00A0 \u00A0  O
| \u00A0 \u00A0 \u00A0 /|\\
| \u00A0 \u00A0 \u00A0 / \\
|
=========''')])
