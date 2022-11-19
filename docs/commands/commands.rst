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

Context
-------

.. attributetable:: slack.commands.Context

.. autoclass:: slack.commands.Context()
    :members:
    :inherited-members:

Command
-------

.. attributetable:: slack.commands.Command

.. autoclass:: slack.commands.Command()
    :members:
    :inherited-members:

Bot
---

.. attributetable:: slack.commands.Bot

.. autoclass:: slack.commands.Bot()
    :members:
    :inherited-members:
    :exclude-members: command, event

    .. automethod:: slack.commands.Bot.command(name=None)
        :decorator:

    .. automethod:: slack.commands.Bot.event()
        :decorator:
