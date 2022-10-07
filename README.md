# An API wrapper with Slack written in Python.

## Key feature
- Modern Pythonic API using async and await.

:warning: This is an alpha version.

## example
```python
import slack

client = slack.Client(
    user_token="...",
    bot_token="...",
    token="..."
)

@client.event
async def on_message(message: slack.Message):
    if message.content.startswith("!"):
        await message.channel.send("Hello.")

@client.event
async def on_channel_create(channel: slack.Channel):
    await channel.send("Hello!")


client.run()
```
### **on_message**
![on_message](https://gyazo.com/cb37b7c67015f0f37a28d0d945dad3c4.png)

### **on_channel_create**
![on_channel_create](https://gyazo.com/40bec93c03343e43dee2180075716d39.png)
