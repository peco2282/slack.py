.. py:currentmodule:: slack

Event Reference
===============

.. py:function:: on_ready()

    Called whenever bow is ready.

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

