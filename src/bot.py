import discord
import os
from dotenv import load_dotenv, find_dotenv
from helper import getSearchKeywordHyperlink

load_dotenv(dotenv_path=find_dotenv())

class BotClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        if(message.author.bot):
            return

        if message.content.startswith('?tag '):
            searchKeyword = ' '.join(message.content.split(' ')[1:]).lower()

            await message.channel.send(getSearchKeywordHyperlink(searchKeyword))    

intents = discord.Intents.default()
intents.message_content = True

client = BotClient(intents=intents)
client.run(os.getenv('BOT_TOKEN', ''))
