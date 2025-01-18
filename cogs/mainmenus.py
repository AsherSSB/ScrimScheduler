import discord
from discord.ext import commands
from custom.ui import ResponseView, ResponseButton


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
        elif view.choice == 0:
            await view.interaction.response.defer()
            await interaction.delete_original_response()
        elif view.choice == 1:
            await view.interaction.response.defer()
            await interaction.delete_original_response()
        elif view.choice == 2:
            await view.interaction.response.defer()
            await interaction.delete_original_response()
        elif view.choice == 3:
            await view.interaction.response.defer()
            await interaction.delete_original_response()
        elif view.choice == 4:
            await view.interaction.response.defer()
            await interaction.delete_original_response()


class ScheduleView(ResponseView):
    def __init__(self):
        super().__init__()
        self.add_item(ResponseButton("View My Schedule", 0, style=discord.ButtonStyle.green, row=0))
        self.add_item(ResponseButton("Set My Availability", 1, style=discord.ButtonStyle.blurple, row=0))
        self.add_item(ResponseButton("Exit", -1, style=discord.ButtonStyle.red, row=4))


class ManagerMenuView(ResponseView):
    def __init__(self):
        super().__init__()
        self.add_item(ResponseButton("Set Open Scrim Times", 0, style=discord.ButtonStyle.blurple, row=1))
        self.add_item(ResponseButton("Send Schedule", 1, style=discord.ButtonStyle.gray, row=1))
        self.add_item(ResponseButton("Exit", -1, style=discord.ButtonStyle.red, row=4))


class AdminMenuView(ResponseView):
    def __init__(self):
        super().__init__()
        self.add_item(ResponseButton("Set Managers", 0, style=discord.ButtonStyle.green, row=3))
        self.add_item(ResponseButton("Exit", -1, style=discord.ButtonStyle.red, row=4))


class SetPotentialTimesView(ResponseView):
    def __init__(self):
        super().__init__()
        self.add_item(ResponseButton("Add Time", 0, style=discord.ButtonStyle.green, row=0))
        self.add_item(ResponseButton("Remove Time", 1, style=discord.ButtonStyle.red, row=0))
        self.add_item(ResponseButton("Back", -1, style=discord.ButtonStyle.red, row=4))


async def setup(bot):
    await bot.add_cog(Scheduler(bot))


