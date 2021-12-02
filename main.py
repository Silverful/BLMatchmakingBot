from discord.ext import commands
from settings import *
import discord
from discord_components import *
from matchmaking import mmdiscord

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=DISCORD_BOT_COMMAND_PREFIX, intents=intents)
DiscordComponents(bot)
for filename in os.listdir("./cogs"):
    if filename.endswith('.py') and filename != '__init__.py':
        bot.load_extension(f'cogs.{filename[:-3]}')


@bot.event
async def on_ready():
    await mmdiscord.fetch_button(bot)

bot.run(DISCORD_BOT_TOKEN)
