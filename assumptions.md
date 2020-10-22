The terms "Flockr owner" and "admin" are equivalent.

**auth_test**


* auth_register
	* It's assumed that the length of first/ last name is 1-50 inclusively
	* Each user has a unique user-id
	* User handle can only consist of alphanumeric characters

* auth_login
    * Every time when a user is logged in, token will be stored in the active_tokens in the database

* auth_login
    * Every time when a user is logged out, token will be removed from the active_tokens in the database
    * If a user try to login multiple times, they will receive the same token instead of a newly generated one

It's assumed that the HTTP wrapper for the above functions are encoded in JSON

**channel_test**

* channel_invite
    * When a user is invited to a channel, they can see any previous messages on the channel before they were invited.
    * Any member in the channel can invite another user into the channel.
    * Inviting a member who is already in the channel is possible, but has no effect.

* channel_join
    * When a user joins a channel, they can see any previous messages on the channel before they were invited.
    * Every channel has a unique channel-id.
    * If a user join a empty channel(For a common user, he can only join the public channel), he automatically becomes the owner of that channel.

* channel_leave
    * When a user leaves a channel, they can no longer access any messages on the channel.
    * If there is one channel left with no member, there is no futher operation needed for this channel.
    * If an owner of the channel is going to leave the channel, he will be removed from the owner list too.
  
* channel_addowner
    * There can be multiple owners of a channel.
    * If there is only one user in the channel, that user automatically becomes the owner.
    * If a user join a channel with no member, he automatically becomes the owner
    * There is no need for a user to be the member of a channel before becoming user of that channel.
  
* channel_removeowner
    * If the owner is the only owner of that channel and been removed, one of other users in that channel randomly be selected to be the next owner.
    * If the owner is the only member of a channel and he wants to remove the owner himself, it will be quivalent to doing the channel_leave operation for this user. In other words, after remove owner himself, he will leave that channel and left with an empty channel.

* channels_create
    * private channels are channels that cannot be joined unless the user is an admin.
    * public channels are channels that can be joined by any user.
    * If a user creates a channel, he/she should be in that channel automatically. Therefore, there will be no channels_join operation for that user.
    * The creator of the channel automatically becomes the owner.
    * Duplicates of channel names are allowed (channel ids are always unique, however)
    * channel names are at least 1 character long (if one tries to create a channel with a empty name, the channel will be called 'new_channel')

* channel_remove
    * For now, this is used as a helper function. It will simply delete the channel from the database without ensuring whether there are users in the channel

* message_send:
    * if the channel doesn't exists, it still raises an AccessError, and not an InputError. It's consistent with the rest of the app, but it's consistent with the spec.
    * raises any AccessError before any InputError. For example, if an unauthorized user (should raise AccessError) sends a 1200 character long message (should raise InputError), an AccessError will be raised.

* message_remove
    * The user can only remove a message that they have sent if they are a member of the channel that they have sent the message in.
    * When a message is removed, it no longer exists in the database
    * You can only remove messages that you have sent.
    * You cannot remove other people's messages (unless you are the owner of the channel)
    * Every message has a unique ID - including messages that are deleted (i.e. a deleted message and an active message cannot have the same ID)
    * An input error also occurs when a message id does not exist (as well as occuring when it no longer exists)

* message_edit
    * The user can only edit a message that they have sent if they are a member of the channel that they have sent the message in.
    * When a message has been edited, there will remain an irremovable text stating that the message has been edited
    to notify the other users.
    * You are only able to edit messages that you have sent.
    * You do not have to be an admin or owner of the channel to edit your message.
    * Spec states an AccessError should be raised if this is not true: "The authorised user is an owner of this channel or the flockr". Therefore, the owner of the flockr or the owner of the channel can edit any message.

**message**

* message_edit
    * Owner of the flock and owner of the channel can edit any message
    * A message that is deleted (empty string) cannot be edited
* user_profile
    * Any valid user can access other users' profile

* search:
    * messages will be sorted by date (newest first)
    * a query string matches a message if the query string is exactly contained within that message (cases matching)
