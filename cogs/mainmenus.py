import discord
from discord.ext import commands
from custom.ui import (
    ResponseView,
    ResponseButton,
    ResponseOption,
    ResponseSelect,
    ResponseSelectView,
    SingleTextSubmission,
    DoubleTextSubmission,
    ConfirmView,
)
from cogs.database import Database
from enum import Enum

SCRIM_TIMES = {
    0: "Monday 8-10pm EST",
    1: "Monday 10-12am EST",
    2: "Tuesday 8-10pm EST",
    3: "Tuesday 10-12am EST",
    4: "Wednesday 8-10pm EST",
    5: "Wednesday 10-12am EST",
    6: "Thursday 8-10pm EST",
    7: "Thursday 10-12am EST",
    8: "Friday 8-10pm EST",
    9: "Friday 10-12am EST",
    10: "Saturday 8-10pm EST",
    11: "Saturday 10-12am EST",
    12: "Sunday 8-10pm EST",
    13: "Sunday 10-12am EST",
}


class PRIVILEGES(Enum):
    PLAYER = 0
    MANAGER = 1
    ADMIN = 2


class Scheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database(bot)

    @discord.app_commands.command(name="schedule")
    async def send_greeting_menu(self, interaction: discord.Interaction):
        user: discord.Member | discord.User = interaction.user
        teams: list[tuple]
        privileges: Enum
        if isinstance(user, discord.Member) and user.guild_permissions.administrator:
            teams = self.db.get_all_teams_from_server_id(interaction.guild_id)
            privileges = PRIVILEGES.ADMIN
        else:
            teams = self.db.get_teams_from_user_id(
                interaction.user.id
            )  # may be issue here properly getting id, name
        view = GreetingView([team[1] for team in teams])
        if isinstance(user, discord.Member) and user.guild_permissions.administrator:
            view.add_item(
                ResponseButton(
                    "Add Team", choice=99, style=discord.ButtonStyle.green, row=3
                )
            )
        await interaction.response.send_message("Welcome!", view=view)
        await view.wait()
        if view.choice == -1:
            await view.interaction.response.defer()
            await interaction.delete_original_response()
        elif view.choice == 99:  # add team
            # send new team name modal
            # update previous interaction for new response in case user clicks out of modal
            pass
        else:
            # TODO: query for privileges
            if self.db.is_manager(teams[view.choice][1], interaction.user.id):
                privileges = PRIVILEGES.MANAGER
            else:
                privileges = PRIVILEGES.PLAYER
            await self.send_main_menu(
                view.interaction, teams[view.choice][1], privileges
            )

    async def send_main_menu(
        self, interaction: discord.Interaction, team_id, privileges
    ):
        view = (
            ScheduleView()
        )  # menu displaying admin and manager buttons inappropriately
        if privileges == PRIVILEGES.MANAGER:
            view.add_item(
                ResponseButton(
                    "Manager Options", 2, style=discord.ButtonStyle.gray, row=1
                )
            )
        elif privileges == PRIVILEGES.ADMIN:
            view.add_item(
                ResponseButton("Admin Options", 3, style=discord.ButtonStyle.red, row=1)
            )
        await interaction.response.send_message("Scrim Scheduler", view=view)
        await view.wait()
        if view.choice == -1:
            await view.interaction.response.defer()
            await interaction.delete_original_response()
        elif view.choice == 0:  # view player's schedule
            await view.interaction.response.defer()
            await interaction.delete_original_response()
        elif view.choice == 1:  # set player's availability
            await view.interaction.response.defer()
            await interaction.delete_original_response()
        elif view.choice == 2:  # view manager menu
            interaction = await self.send_manager_menu(view.interaction, team_id)
            await self.send_main_menu(interaction, team_id, privileges)
        else:  # view admin menu
            await view.interaction.response.defer()
            await interaction.delete_original_response()

    async def send_manager_menu(self, interaction: discord.Interaction, team_id):
        view = ManagerMenuView()
        await interaction.response.send_message("Manager Menu", view=view)
        await view.wait()

        while view.choice != -1:
            if view.choice == 0:
                interaction = await self.send_set_times_view(view.interaction, team_id)
            view = ManagerMenuView()
            await interaction.edit_original_response(view=view)
            await view.wait()

        return view.interaction

    async def send_set_times_view(self, interaction: discord.Interaction, team_id):
        view = SetPotentialTimesView()
        times = []
        await interaction.response.send_message("Set Times", view=view)
        await view.wait()
        while view.choice != -1 and view.choice != 0:
            # set times to selections
            times = view.selections
            # reset view
            view = SetPotentialTimesView()
            content = ""
            for time in times:
                content += SCRIM_TIMES[time] + "\n"
            # edit response with selections and new view
            await interaction.edit_original_response(content=content, view=view)
            # wait for response
            await view.wait()
        if view.choice == 0:
            # set time
            self.db.set_team_scrim_blocks(team_id, "")
            # return interaction
        return view.interaction

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
        self.add_item(
            ResponseButton("My Schedule", 0, style=discord.ButtonStyle.green, row=0)
        )
        self.add_item(
            ResponseButton(
                "Set My Availability", 1, style=discord.ButtonStyle.blurple, row=0
            )
        )
        self.add_item(ResponseButton("Exit", -1, style=discord.ButtonStyle.red, row=4))


class ManagerMenuView(ResponseView):
    def __init__(self):
        super().__init__()
        self.add_item(
            ResponseButton(
                "Set Open Scrim Times", 0, style=discord.ButtonStyle.blurple, row=1
            )
        )
        self.add_item(
            ResponseButton("Send Schedule", 1, style=discord.ButtonStyle.gray, row=1)
        )
        self.add_item(ResponseButton("Back", -1, style=discord.ButtonStyle.red, row=4))


class AdminMenuView(ResponseView):
    def __init__(self):
        super().__init__()
        self.add_item(
            ResponseButton("Set Managers", 0, style=discord.ButtonStyle.green, row=3)
        )
        self.add_item(
            ResponseButton("Create Team", 1, style=discord.ButtonStyle.blurple, row=3)
        )
        self.add_item(
            ResponseButton("Disband Team", 2, style=discord.ButtonStyle.red, row=3)
        )
        self.add_item(ResponseButton("Back", -1, style=discord.ButtonStyle.red, row=4))


class SetPotentialTimesView(ResponseSelectView):
    def __init__(self):
        super().__init__()
        select_items = []
        for keys, values in SCRIM_TIMES.items():
            select_items.append(ResponseOption(values, keys))
        self.add_item(ResponseSelect(select_items, 0))


async def setup(bot):
    await bot.add_cog(Scheduler(bot))
