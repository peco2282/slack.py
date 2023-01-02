.. currentmodule:: slack.view

API Reference
===============

The following section outlines the API of slack.py.

.. note::
    `View` is slack.Channel#send() 's parameter.

    .. code-block:: python

        import slack
        from slack import commands
        from slack import view

        bot = commands.Bot(...)

        @bot.command(name="hello")
        async def hello(ctx: commands.Context, *args):
            option1 = view.SelectOption(
                "hello1",
                "option1"
            )

            option2 = view.SelectOption(
                "hello2",
                "option2"
            )
            aview = view.ActionView(option1, option2)
            sview = view.SectionView(b, "option with sectionview.")
            view = View(aview, sview)

            await ctx.send(view=view)


.. toctree::
    :caption: Table of view Contents.
    :maxdepth: 1

    models