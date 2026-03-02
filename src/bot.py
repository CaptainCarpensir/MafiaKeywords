import discord
from discord import app_commands
import os
#import sys
from dotenv import load_dotenv, find_dotenv
from helper import getTag, addTag, removeTag

load_dotenv(dotenv_path=find_dotenv())

HOST_ROLE = 1157534411982643220

def is_host(interaction: discord.Interaction) -> bool:
    return any(role.id == HOST_ROLE for role in interaction.user.roles)

class AdditionalNotesButton(discord.ui.View):
    def __init__(self, notes: list):
        super().__init__()
        for note in notes:
            url = note['url']
            label = note.get('label', 'Additional Notes')

            async def notes_callback(interaction: discord.Interaction, u=url):
                embed = discord.Embed()
                embed.set_image(url=u)
                await interaction.response.send_message(embed=embed, ephemeral=True)

            button = discord.ui.Button(label=label, style=discord.ButtonStyle.secondary)
            button.callback = notes_callback
            self.add_item(button)

# Go my terrible fuckass type hints
def build_tag_response(entry: dict) -> tuple[str | None, discord.Embed | None, discord.ui.View | None]:
    url = entry.get('url', '')
    notes = entry.get('notes')

    # Some meme tags have only text instead of a url and have to be handled separately because they hate me
    parts = url.split()
    image_url = next((p for p in parts if p.startswith('http')), None)

    if not image_url:
        return url, None, None

    prefix = url[:url.index(image_url)].strip() or None
    embed = discord.Embed(description=prefix)
    embed.set_image(url=image_url)
    view = AdditionalNotesButton(notes) if notes else None
    return None, embed, view


class BotClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content.startswith('?tag '):
            searchKeyword = ' '.join(message.content.split(' ')[1:]).lower()
        elif message.content.startswith('?') and not message.content.startswith('??') and len(set(message.content)) > 1:
            searchKeyword = (message.content[1:]).lower()
        else:
            return

        entry = getTag(searchKeyword)

        if entry is None:
            await message.channel.send("No match found.")
            return

        text, embed, view = build_tag_response(entry)

        if text:
            await message.channel.send(text)
        else:
            await message.channel.send(embed=embed, view=view)

client = BotClient()

@client.tree.command(name="add_tag", description="Add a new tag.")
@app_commands.describe(
    url="The URL this tag should return.",
    keywords="Comma-separated list of keywords. COMMA SEPARATED.",
    notes="(Optional) Additional notes link."
)
async def add_tag(interaction: discord.Interaction, url: str, keywords: str, notes: str = None):
    if not is_host(interaction):
        await interaction.response.send_message("This command is only available to HOSTS.", ephemeral=True)
        return

    # Okay if you made it here you're an actual host now
    keyword_list = [kw.strip().lower() for kw in keywords.split(',') if kw.strip()]

    if not keyword_list:
        await interaction.response.send_message("Tag must have at least one keyword.", ephemeral=True)
        return

    addTag(url, keyword_list, notes)

    formatted = ', '.join(f'`{kw}`' for kw in keyword_list)
    await interaction.response.send_message(
        f"Tag for keywords \"{formatted}\" added.",
        ephemeral=False
    )

@client.tree.command(name="remove_tag", description="Remove a tag by one of its keywords.")
@app_commands.describe(keyword="One keyword from the tag to remove.")
async def remove_tag(interaction: discord.Interaction, keyword: str):
    if not is_host(interaction):
        await interaction.response.send_message("This command is only available to HOSTS.", ephemeral=True)
        return

    # Okay if you made it here you're an actual host now
    if removeTag(keyword):
        await interaction.response.send_message(
            f"Tag with keyword `{keyword.strip().lower()}` has been removed.",
            ephemeral=False
        )
    else:
        await interaction.response.send_message(
            f"No tag found with keyword `{keyword.strip().lower()}`",
            ephemeral=True
        )

client.run(os.getenv('BOT_TOKEN', ''))
