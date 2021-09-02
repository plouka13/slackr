# Assumptions.md

##General
Assume that all the other functions work besides the one being tested.
Assume an empty string is not a valid ID for user or channel.
Assume appending ‘bad’ to a token or channel_id makes it invalid.

## Auth
**auth_register**: If no error is raised, we assume the function was successful and a user is registered and given a token. Since it is a base function that everything else depends on, we cannot test much deeper.

**auth_login**: A user can login after registering, thus creating 2 active sessions (Piazza stated this may be clarified after iteration1). One test assumes auth_logout works.

**auth_logout**: auth_register and auth_login both work

## Channel
**channel_join**: Slackr owner can join a private channel.

**channel_invite**: Users can be invited to a channel they are already in (no change occurs). No change occurs if the user invites him/herself. Any channel member can send an invite, regardless of permissions in a private channel. 

**channel_message**: Assuming token is member or owner of channel with channel_id. Owner of slackr will be able to run channel_messages with no errors. Start cannot be anything but -1, or a positive integer. End cannot be anything but -1 or a positive integer.

**channel_leave**: A channel does not get destroyed when the channel owner leaves (ownership does not automatically switch). 

**channel_addowner**: Adding an owner automatically makes the user also a member of the channel. Input error when target u_id does not exist. Input error (rather than access error) when a channel member (nonowner) calls addowner on a u_id who is already a channel owner. (Note this could also be an access error)

**channel_removeowner**: Removing an owner keeps them as a member. Owners can remove themselves as owners (resulting in non empty but ownerless channels). Channel owners can remove Slackr owner’s owner status for the channel.

## Channels
No specific assumptions
## Message
**message_send** : An empty message sends as a valid message. User sending the message is in the channel. Assumes messages is a valid dictionary. Invalid channel ID throws InputError

**message_remove** :  Assumes the token owns the channel or sent the message.  Assumes there is a message with message_id to remove (no invalid message_id is given). Can only remove one message at a time. Assumes message_id cannot be the same as any other channel messages. 

**message_edit** : Assumes the token owns the channel or sent the message.  Assumes there is a message with message_id to edit (no invalid message_id is given). Can only edit one message at a time. Assumes message_id cannot be the same as any other channel messages. Assumes messages is a valid dictionary.

## Users
**User_profile**: Assumes that handles are between 3 and 20 characters inclusive of 3 and 20. 
Assumes when dealing with handles of people with similar/the same name which will produce the same default handle, a consecutively increasing number starting at 1 will be attached to the end of the handle to ensure there are no repeated handles.
Assumes that if a user has single character first and last names that a number will be attached to the end of their handle upon registration so it fits the minimum handle length.
Assumes that repeat handles which are 20 characters long will be further truncated accordingly to allow for a single digit or larger number to be put on the end.

**Users_profile_setname**: Assumes that set name is between 1 and 50 inclusive of 1 and 50. 
Assumes that if input given is just spaces, no change will be made.
Assumes that numbers cannot be apart of first or last names.
Assumes that the hyphen, apostrophe and space characters are valid when contained in a name, but all other special characters are not, and no change will be made if names contain them, or if the hyphen, apostrophe or space are at the beginning or end of a name.
Assumes that leading or trailing spaces in names should be removed, and not considered in the overall length of a name. 
Assumes that if one of the proposed names is valid but the other isn’t, that neither will be changed.

**Users_profile_sethandle**:
Assumes that handles may contain capitalisation, spaces, numbers and special characters, Assumes that handles are between 3 and 20 characters inclusive of 3 and 20.
Assumes that a handle cannot exclusively contain spaces and that all leading and trailing spaces in a handle will be removed and not factored in when sizing the length of a string. 
If a user tries to set their username to a taken username spelt with different capitalisation they will still be regarded as the same string and cause an input error.
**Users_profile_setemail**: Assuming emails and valid / invalid based on requirements given, not new method was devised. 
Assuming that since emails aren’t case sensitive, capitalisation should be ignored when checking if an email is already is use. 
## Other

**Users_all**: Assumes that users are added immediately into the list when registered.
Hence assumes the ordering of the list is solely based on when a user registered into slackr.
Assumes that the list will supply all registered users regardless of whether they are logged in or out.
Assumes that the users list user_profile dictionaries will be updated when user profiles are updated, but no change to list ordering will occur.

**Search**: It is assumed that the search function isn’t case sensitive, e.g. searching for “HELLO” may return results saying “hello”. 
It’s assumed that the ID returned in the messages list is the ID of the user who produced the searched for string at a given not, that the ID of the user who is calling the search function.
It assumes that the only strings the caller will be able to reach are in channels they are currently joined in, not channels they are not members of and not channels they have left.
It assumes that the caller will be able to access the entire backlog of messages of channels they are currently in, regardless of when they joined the channels.
It assumes that the search function will be unable to find deleted strings, or the original versions of edited strings.
