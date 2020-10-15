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

**channel_test**

* channel_invite
    * When a user is invited to a channel, they can see any previous messages on the channel before they were invited.
    * Any member in the channel can invite another user into the channel.
    * Inviting a member who is already in the channel is possible, but has no effect.

* channel_join
    * When a user joins a channel, they can see any previous messages on the channel before they were invited.
    * Every channel has a unique channel-id.

* channel_leave
    * When a user leaves a channel, they can no longer access any messages on the channel.

* channel_addowner
    * There can be multiple owners of a channel.
    * If there is only one user in the channel, that user automatically becomes the owner.

* channel_removeowner
    * If the owner is the only owner of that channel and been removed, one of other users in that channel randomly be selected to be the next owner.
    * If the owner is the only member of a channel and been removed, the channel is also removed. For now, there is no way to remove a whole channel. Therefore, we leave the channel without owner in this situation.

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
    * Removing a message leaves another message on the channel stating "This message has been removed" to indicate
    that a messsage has been deleted to other users.
    * You can only remove messages that you have sent.
    * You cannot remove other people's messages.
    * Every message has a unique ID - including messages that are deleted (i.e. a deleted message and an active message cannot have the same ID)
    * An input error also occurs when a message id does not exist (as well as occuring when it no longer exists)

* message_edit
    * When a message has been edited, there will remain an irremovable text stating that the message has been edited
    to notify the other users.
    * You are only able to edit messages that you have sent.
    * You do not have to be an admin or owner of the channel to edit your message.

