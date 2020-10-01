**auth_test**


* auth_register
	* It's assumed that the length of first/ last name is 1-50 inclusively
	* Each user has a unique user-id
	* User handle can only consist of alphanumeric characters

* auth_login
    * Every time when a user is logged in, token will be stored in the active_tokens in the database

* auth_login
    * Every time when a user is logged out, token will be removed from the active_tokens in the database
**channel_test**

* channel_join
    * When a user is invited to channel, they can see any previous messages on the channel before they were invited.
    * Every channel has a unique channel-id. Channel-ids are also unique from user-ids and vice versa.

* channel_leave
    * When a user leaves a channel, they can no longer access any messages on the channel.

* channel_addowner
    * There can be multiple owners of a channel.
    * If there is only one user in the channel, that user automatically becomes the owner.

* channel_removeowner
    * If the owner is removed from a channel, another user in the channel is 
    randomly selected to be the next owner unless specified.
    * If the owner is removed from the channel and the owner is the only user in that channel, the channel is also removed.

* channels_create
    * private channels are channels that cannot be joined unless the user is an admin.
    * public channels are channels that can be joined by any user.
    * If a user creates a channel, he/she should be in that channel automatically. Therefore, there will be no channels_join operation for that user.
    * The creator of the channel automatically becomes the owner.
    * Duplicates of channel names are allowed

* channel_remove
    * For now, this is used as a helper function. It will simply delete the channel from the database without ensuring whether there are users in the channel
    
* message_remove
    * Removing a message leaves another message on the channel stating "This message has been removed" to indicate
    that a messsage has been deleted to other users.
    * You can only remove messages that you have sent.
    * You cannot remove other people's messages.

* message_edit
    * When a message has been edited, there will remain an irremovable text stating that the message has been edited
    to notify the other users.
    * You are only able to edit messages that you have sent.
    * You do not have to be an admin or owner of the channel to edit your message.

