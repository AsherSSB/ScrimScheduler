import discord
from discord.ext import commands
from cogs.database import Database


class Testing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database(bot)


async def setup(bot):
    await bot.add_cog(Testing(bot))
