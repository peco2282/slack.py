.. py:currentmodule:: slack.commands

Event Reference
===============

.. py:function:: on_command(ctx)

    Called whenever a command was invoked.

    :param ctx: The sended context.
    :type ctx: :class:`Context`


.. py:function:: on_invoke(ctx)

    An alias for `on_command()`.

    :param ctx: The sended context.
    :type ctx: :class:`Context`

.. py:function:: on_command_error(ctx, err)

    Called whenever error occured.

    :param ctx: The sended context.
    :type ctx: :class:`Context`
    :param err: Raised exception from sended context.
    :type err: :class:`Exception`
