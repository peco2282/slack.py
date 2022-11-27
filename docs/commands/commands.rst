.. currentmodule:: slack.commands

Commands Object
===============

.. note:: This `commands` object is an extention of basic-client.

    Usage..

    .. code-block:: python

        from slack import commands

        client = commands.Client(..., prefix="!")

        @client.command(name="msg")
        async def message(ctx: commands.Context, *args):
            await ctx.channel.send("message received!")

        @client.command()
        async def ping(ctx: commands.Context, *args):
            await ctx.channel.send("pong!")


    If commands was start your prefix and the command was registered, dispatch command-function.


Bot
---

This class need...

- user-token.
- bot-token.
- app-token.
- prefix.

Prefix is a string for command occur.
If you don't need this, you put `prefix=""`

.. attributetable:: slack.commands.Bot

.. autoclass:: slack.commands.Bot()
    :members:
    :inherited-members:
    :exclude-members: command, event

    .. automethod:: slack.commands.Bot.command(name=None)
        :decorator:

    .. automethod:: slack.commands.Bot.event()
        :decorator:

Context
-------

.. attributetable:: slack.commands.Context

.. autoclass:: slack.commands.Context()
    :members:
    :inherited-members:

Command
-------
.. note:: If raise exception in commands object, it will go to `on_command_error(ctx, err)`
    event.

.. attributetable:: slack.commands.Command

.. autoclass:: slack.commands.Command()
    :members:
    :inherited-members:
