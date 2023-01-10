.. currentmodule:: slack

.. _api-events:

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

.. function:: on_ready()

    Called whenever bot is ready.

Messages
--------

.. function:: on_message(message)

    Called whenever a message was sent.

    :param message: The sended message.
    :type message: :class:`Message`


.. function:: on_message_update(before, after)

    Called whenever a message was updated.

    :param before: The sended message.
    :type before: :class:`Message`
    :param after: The sended message.
    :type after: :class:`Message`


.. function:: on_message_delete(message)

    Called whenever a message was deleted.

    :param message: The deleted message.
    :type message: :class:`DeletedMessage`

.. py:function:: on_mention(message)

    Called whenever mention(s) in message.

    :param message: Sended message.
    :type message:  :class:`Message`

.. py:function:: on_block_action(block)

    Called whenever message action occured.

    :param block: The block data.
    :type block: :class:`Block`

.. function:: on_channel_join(message)

    Called whenever a message was sent at member was joined.

    :param message: The deleted message.
    :type message: :class:`JoinMessage`


.. function:: on_reaction_added(author, member, event)

    Called whenever a reaction was added.

    :param author: Reacted message author.
    :type author: :class:`Member`
    :param member: Reacted member.
    :type member: :class:`Member`
    :param event: Reaction information.
    :type event: :class:`ReactionEvent`

.. function:: on_reaction_removed(author, member, event)

    Called whenever a reaction was removed.

    :param author: Unreacted message author.
    :type author: :class:`Member`
    :param member: Unreacted member.
    :type membner: :class:`Member`
    :param event: Reaction information.
    :type event: :class:`ReactionEvent`

Channels
--------

.. function:: on_channel_create(channel)

    Called whenever channel was created.

    :param channel: The created channel.
    :type channel: :class:`Channel`

.. function:: on_channel_delete(channel)

    Called whenever channel was deleted.

    :param channel: The deleted channel.
    :type channel: :class:`DeletedChannel`

.. function:: on_channel_rename(before, after)

    Called whenever channel was renamed.

    :param before: The renamed channel(before).
    :type before: :class:`Channel`
    :param after: The renamed channel(after).
    :type after: :class:`Channel`

.. function:: on_channel_unarchive(channel, user)

    Called whenever channel was unarcchived.

    :param channel: The unarchived channel.
    :type channel: :class:`Channel`
    :param user: The member who channel unarchive.
    :type user: :class:`Member`

.. function:: on_member_join(channel, user)

    Called whenever member joined channel.

    :param channel: The member joined channel.
    :type channel: :class:`Channel`
    :param user: The joined member.
    :type user: :class:`Member`

