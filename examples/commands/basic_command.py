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
    await ctx.channel.send("message received! " + ",".join(args))


@bot.command()
async def ping(ctx: commands.Context, *args):
    await ctx.channel.send("pong! with " + ", ".join(args))


bot.run()
