import slack


class MyClient(slack.Client):
    def __init__(
            self,
            user_token: str = "xoxp-...",
            bot_token: str = "xoxb-...",
            token: str = "xapp-...",
    ):
        super().__init__(
            user_token,
            bot_token,
            token,
        )

    async def on_ready(self):
        print("Bot is ready.")

    async def on_message(self, message: slack.Message):
        if message.author.bot:
            return

        if message.content.startswith("!hello"):
            await message.channel.send(f"Hello! {message.author.name}")

    async def on_channel_create(self, channel: slack.Channel):
        await channel.send("Hello!")


MyClient().run()
