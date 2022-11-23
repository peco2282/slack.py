.. py:currentmodule:: slack.commands

Event Reference
===============

.. py:function:: on_command_error(ctx, err)

    Called whenever a message was sent.

    :param ctx: The sended context.
    :type message: :class:`Context`
    :param err: Raised exception from sended context.
    :type err: :class:`Exception`
