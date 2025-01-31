import discord
from discord.ext import commands
from custom.ui import ResponseView, ResponseButton, SingleTextSubmission, DoubleTextSubmission, ConfirmView
from cogs.database import Database


class Scheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database(bot)

    @discord.app_commands.command(name="schedule")
    async def send_greeting_menu(self, interaction: discord.Interaction):
        # if user is admin, query all teams related to server id
        teams: list[tuple]
        if interaction.user.guild_permissions.administrator:
            teams = self.db.get_all_teams(interaction.guild_id)
        # else query all teams where server and user are related
        else:
            # placeholder
            teams = []
        # initialize view with team options
        view = GreetingView([team[1] for team in teams])
        # if user is admin, add add team button to view
        if interaction.user.guild_permissions.administrator:
            view.add_item(ResponseButton("Add Team", choice=99, style=discord.ButtonStyle.green, row=3))
        # respond to interaction with view
        await interaction.response.send_message("Welcome!", view=view)
        # wait for selection
        await view.wait()
        if view.choice == -1:
            await interaction.delete_original_response()
        # if option is add team, send add team dialogue
        elif view.choice == 99:
            # send new team name modal
            # update previous interaction for new response in case user clicks out of modal
            pass
        else:
            # send selected team menu
            pass

    async def send_main_menu(self, interaction: discord.Interaction):
        view = ScheduleView()
        await interaction.response.send_message("Scrim Scheduler", view=view)
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
            interaction = await self.send_manager_menu(view.interaction)
            await self.send_main_menu(interaction)
        else:
            await view.interaction.response.defer()
            await interaction.delete_original_response()

    async def send_manager_menu(self, interaction: discord.Interaction):
        view = ManagerMenuView()
        interaction.response.send_message("Manager Menu", view=view)
        await view.wait()
        if view.choice == -1:
            return view.interaction
        elif view.choice == 0:
            interaction = await self.send_set_times_view(view.interaction)
            await self.send_manager_menu(interaction)

    async def send_set_times_view(self, interaction: discord.Interaction):
        view = SetPotentialTimesView()
        await interaction.response.send_message("Set Scrim Times", view=view)
        await view.wait()
        if view.choice == -1:
            return view.interaction
        elif view.choice == 0:
            modal = DoubleTextSubmission("Set Scrim Time", "Date/Day of The Week", "Time")
            await view.interaction.response.send_modal(modal)
            await modal.wait()
            interaction = modal.interaction
            time = f"{modal.first_input}, {modal.second_input}"
            view = ConfirmView()
            await interaction.response.send_message(f"Add \"{time}\"?")
            await view.wait
            if view.choice == -1:
                await self.send_set_times_view(view.interaction)
            else:
                # TODO: add time to database
                await self.send_set_times_view(view.interaction)

    async def cleanup(self):
        self.db.conn.close
        self.db.cur.close

    async def cog_unload(self):
        await self.cleanup()


class GreetingView(ResponseView):
    def __init__(self, team_names: list[str]):
        super().__init__()
        for i, name in enumerate(team_names):
            self.add_item(ResponseButton(name, i))
        self.add_item(ResponseButton("exit", -1, style=discord.ButtonStyle.red, row=4))


class ScheduleView(ResponseView):
    def __init__(self):
        super().__init__()
        self.add_item(ResponseButton("My Schedule", 0, style=discord.ButtonStyle.green, row=0))
        self.add_item(ResponseButton("Set My Availability", 1, style=discord.ButtonStyle.blurple, row=0))
        self.add_item(ResponseButton("Manager Options", 2, style=discord.ButtonStyle.gray, row=1))
        self.add_item(ResponseButton("Admin Options", 3, style=discord.ButtonStyle.red, row=1))
        self.add_item(ResponseButton("Exit", -1, style=discord.ButtonStyle.red, row=4))


class ManagerMenuView(ResponseView):
    def __init__(self):
        super().__init__()
        self.add_item(ResponseButton("Set Open Scrim Times", 0, style=discord.ButtonStyle.blurple, row=1))
        self.add_item(ResponseButton("Send Schedule", 1, style=discord.ButtonStyle.gray, row=1))
        self.add_item(ResponseButton("Back", -1, style=discord.ButtonStyle.red, row=4))


class AdminMenuView(ResponseView):
    def __init__(self):
        super().__init__()
        self.add_item(ResponseButton("Set Managers", 0, style=discord.ButtonStyle.green, row=3))
        self.add_item(ResponseButton("Create Team", 1, style=discord.ButtonStyle.blurple, row=3))
        self.add_item(ResponseButton("Disband Team", 2, style=discord.ButtonStyle.red, row=3))
        self.add_item(ResponseButton("Back", -1, style=discord.ButtonStyle.red, row=4))


class SetPotentialTimesView(ResponseView):
    def __init__(self):
        super().__init__()
        self.add_item(ResponseButton("Add Time", 0, style=discord.ButtonStyle.green, row=0))
        self.add_item(ResponseButton("Remove Time", 1, style=discord.ButtonStyle.red, row=0))
        self.add_item(ResponseButton("Back", -1, style=discord.ButtonStyle.red, row=4))


async def setup(bot):
    await bot.add_cog(Scheduler(bot))


