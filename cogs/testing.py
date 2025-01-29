import discord
from discord.ext import commands
from cogs.database import Database


class Testing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database(bot)

    @discord.app_commands.command(name="testdb")
    async def get_teams_test(self, interaction: discord.Interaction):
        teams = self.db.get_teams(interaction.guild_id)
        await interaction.response.send_message(teams)


async def setup(bot):
    await bot.add_cog(Testing(bot))


