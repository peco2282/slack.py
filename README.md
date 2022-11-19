![PyPI](https://img.shields.io/pypi/v/wsslack.py)
![PyPI - License](https://img.shields.io/pypi/l/wsslack.py)

# An API wrapper with Slack written in Python.

## Key feature
- Modern Pythonic API using `async` and `await`.
- API and interactive components of the platform  by utilizing websockets.

[//]: # (:warning: This is an alpha version.)

[**Document**](https://slack-py.readthedocs.io/en/latest/)

## Install

```shell
$ pip install wsslack.py
```


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

## extentional usage.
If you use app with commands..

```python
from slack import commands

bot = commands.Bot(..., prefix="!")

@bot.command(name="msg")
async def message(ctx: commands.Context, *args):
    await ctx.channel.send("message received!")

@bot.command()
async def ping(ctx: commands.Context, *args):
    await ctx.channel.send("pong!")
```

![msg](https://gyazo.com/38adfa4b18775e894d8c6f47d17d62f3.png)

![ping](https://gyazo.com/0f68ed0f4a125a2220782d703de0f24f.png)
