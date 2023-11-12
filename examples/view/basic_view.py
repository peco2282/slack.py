import slack
from slack.view import SelectType, Text, Select

client = slack.Client(
    user_token="...",
    bot_token="...",
    token="..."
)


@client.event
async def on_ready():
    print("Bot is ready.")


@client.event
async def on_message(message: slack.Message):
    if message.author.bot:
        return

    if message.content.startswith("!hello"):
        select = Select(
            "action",
            placeholder=Text(
                "text", mrkdown=False, emoji=True),
            select_type=SelectType.users_select,
            initial_text="initial"
        )

        view = View(select)
        await message.channel.send(view=view)


client.run()
