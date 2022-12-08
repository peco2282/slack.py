from slack import commands
from slack.view import View, Select, Placeholder, SelectType

bot = commands.Bot(
    user_token="...",
    bot_token="...",
    token="...",
    prefix="!"
)


@bot.event
async def on_ready():
    print(f"bot is ready")


@bot.command()
async def msg(ctx: commands.Context, *args):
    # m = await ctx.send(text="AA")
    select = Select(
        "action",
        Placeholder(
            "text", mrkdwn=False, emoji=True),
        select_type=SelectType.users_select,
        initial_text="initial"
    )

    view = View(select)
    await ctx.send(view=view)


bot.run()
