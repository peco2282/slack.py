import slack

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
        await message.channel.send(f"Hello! {message.author.name}")


@client.event
async def on_channel_create(channel: slack.Channel):
    await channel.send("Hello!")


@client.event
async def on_channel_unarchive(channel: slack.Channel, user: slack.Member):
    await channel.send_as_user(f"{user.name} unarchive this channel.")


client.run()
