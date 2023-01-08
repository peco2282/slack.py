import asyncio

import slack
from slack import commands

bot = commands.Bot(
    user_token="xoxp-...",
    bot_token="xapp-...",
    token="xoxb-...",
    prefix="!"
)


@bot.event
async def on_ready():
    print("App is ready!")


@bot.command(name="msg")
async def message(ctx: commands.Context, *args):
    def check(msg: slack.Message):
        return ctx.author == msg.author

    while True:
        try:
            bot.wait_for("message", check=check, timeout=30)

        except asyncio.TimeoutError:
            break

        else:
            await ctx.channel.send("message received! " + ",".join(args))


bot.run()
