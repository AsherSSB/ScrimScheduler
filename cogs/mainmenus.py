import discord
from discord.ext import commands
import asyncio


class Scheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="schedule")
    async def test_send_main_menu(self, interaction: discord.Interaction):
        view = ScheduleView()
        await interaction.response.send_message("Hello World!", view=view)
        await view.wait()
        if view.choice == -1:
            await view.interaction.response.defer()
            await interaction.delete_original_response()
        # TODO: add functionality to other choices
        else:
            await view.interaction.defer()
            pass


class ScheduleView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.choice: int
        self.interaction: discord.Interaction
        self.event = asyncio.Event()

    @discord.ui.button(label="exit", style=discord.ButtonStyle.red)
    async def back_button(self, interaction: discord.Interaction, button):
        self.choice = -1
        self.event.set()
        self.interaction = interaction

    async def wait(self):
        await self.event()


async def setup(bot):
    await bot.add_cog(Scheduler(bot))


