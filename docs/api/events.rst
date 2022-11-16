.. py:currentmodule:: slack

Event Reference
===============

.. note:: Events usage.

    .. code-block:: python

        import slack

        client = slack.Client(...)

        @client.event
        async def on_message_update(before: slack.Message, after: slack.Message):  # Event name.
            print(before.content, after.content)
            # Statements...


Ready
-----

.. py:function:: on_ready()

    Called whenever bot is ready.

Messages
--------

.. py:function:: on_message(message)

    Called whenever a message was sent.

    :param message: The sended message.
    :type message: :class:`Message`


.. py:function:: on_message_update(before, after)

    Called whenever a message was updated.

    :param before: The sended message.
    :type before: :class:`Message`
    :param after: The sended message.
    :type after: :class:`Message`


.. py:function:: on_message_delete(message)

    Called whenever a message was deleted.

    :param message: The deleted message.
    :type message: :class:`DeletedMessage`


.. py:function:: on_channel_join(message)

    Called whenever a message was sent at member was joined.

    :param message: The deleted message.
    :type message: :class:`JoinMessage`


.. py:function:: on_channel_archive(message)

    Called whenever a channel was archived.

    :param message: The sent message when channel was archived.
    :type message: :class:`ArchivedMessage`

Channels
--------

.. py:function:: on_channel_create(channel)

    Called whenever channel was created.

    :param channel: The created channel.
    :type channel: :class:`Channel`

.. py:function:: on_channel_delete(channel)

    Called whenever channel was deleted.

    :param channel: The deleted channel.
    :type channel: :class:`DeletedChannel`

.. py:function:: on_channel_rename(before, after)

    Called whenever channel was renamed.

    :param before: The renamed channel(before).
    :type before: :class:`Channel`
    :param after: The renamed channel(after).
    :type after: :class:`Channel`

.. py:function:: on_channel_unarchive(channel, user)

    Called whenever channel was unarcchived.

    :param channel: The unarchived channel.
    :type channel: :class:`Channel`
    :param user: The member who channel unarchive.
    :type user: :class:`Member`

.. py:function:: on_member_join(channel, user)

    Called whenever member joined channel.

    :param channel: The member joined channel.
    :type channel: :class:`Channel`
    :param user: The joined member.
    :type user: :class:`Member`

.. py:function:: on_reaction_add(user, item_user, react_type)

    Called whenever reaction added.

    :param user: The reacted member.
    :type user: :class:`Member`
    :param item_user: The reaction owner.
    :type item_user: :class:`Member`
    :param react_type: The reaction data.
    :type react_type: :class:`ReactionEventType`

.. py:function:: on_reaction_remove(user, item_user, react_type)

    Called whenever reaction was removed.

    :param user: The reacted member.
    :type user: :class:`Member`
    :param item_user: The reaction owner.
    :type item_user: :class:`Member`
    :param react_type: The reaction data.
    :type react_type: :class:`ReactionEventType`
