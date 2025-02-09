import discord
from discord.ext import commands
from custom.ui import (
    ResponseView,
    ResponseButton,
    ResponseOption,
    ResponseSelect,
    ResponseSelectView,
    ResponseModalHandler,
    SingleTextSubmission,
    DoubleTextSubmission,
    ConfirmView,
)
from cogs.database import Database
from enum import Enum
from dataclasses import dataclass, asdict
from jsonpickle import encode as pickle, decode as unpickle

SCRIM_TIMES = {
    0: "6:00 - 8:00 EST",
    1: "6:30 - 8:30 EST",
    2: "7:00 - 9:00 EST",
    3: "7:30 - 9:30 EST",
    4: "8:00 - 10:00 EST",
    5: "8:30 - 10:30 EST",
    6: "9:00 - 11:00 EST",
    7: "9:30 - 11:30 EST",
    8: "10:00 - 12:00 EST",
}

SCRIM_DAYS = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}


@dataclass
class Schedule:
    monday: list
    tuesday: list
    wednesday: list
    thursday: list
    friday: list
    saturday: list
    sunday: list

    def __len__(self):
        return len(asdict(self))  # no. days in week


class PRIVILEGES(Enum):
    PLAYER = 0
    MANAGER = 1
    ADMIN = 2


class Scheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database(bot)

    @discord.app_commands.command(name="schedule")
    async def initialize_app(self, interaction: discord.Interaction):
        await self.send_greeting_menu(interaction)

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
        if view.choice == -1:  # exit
            await view.interaction.response.defer()
            await interaction.delete_original_response()
        elif view.choice == 99:  # add team
            # send new team name modal
            await self.send_team_creation_menu(interaction, view.interaction)
        else:  # selected a team
            if privileges == PRIVILEGES.ADMIN:
                pass
            elif self.db.is_manager(teams[view.choice][1], interaction.user.id):
                privileges = PRIVILEGES.MANAGER
            else:
                privileges = PRIVILEGES.PLAYER
            await interaction.delete_original_response()
            await self.send_main_menu(
                view.interaction, teams[view.choice][1], privileges
            )

    async def send_team_creation_menu(self, old_interaction, fresh_interaction):
        handler = ResponseModalHandler(
            "Create New Team",
            old_interaction,
            fresh_interaction,
            "Team Name",
        )
        interaction, responses = await handler.send_response_modal()
        if responses:
            self.db.create_team(
                interaction.guild_id, responses["Team Name"]
            )  # responses 0 is team name
        await self.send_greeting_menu(interaction)

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
                ResponseButton(
                    "Manager Options", 2, style=discord.ButtonStyle.gray, row=1
                )
            )
            view.add_item(
                ResponseButton("Admin Options", 3, style=discord.ButtonStyle.red, row=1)
            )
        await interaction.response.send_message("Scrim Scheduler", view=view)
        await view.wait()
        if view.choice == -1:  # back to welcome menu
            await interaction.delete_original_response()
            await self.send_greeting_menu(view.interaction)
        # TODO: implement team schedule view
        elif view.choice == 0:  # view player's schedule
            await view.interaction.response.defer()
            await interaction.delete_original_response()
        # TODO: implement set availability for players
        elif view.choice == 1:  # set player's availability
            await view.interaction.response.defer()
            await interaction.delete_original_response()
        # TODO: implement manager menu
        elif view.choice == 2:  # view manager menu
            await interaction.delete_original_response()
            interaction = await self.send_manager_menu(view.interaction, team_id)
            await self.send_main_menu(interaction, team_id, privileges)
        # TODO: implement admin menu
        else:  # view admin menu
            await view.interaction.response.defer()
            await interaction.delete_original_response()

    async def send_manager_menu(self, interaction: discord.Interaction, team_id):
        view = ManagerMenuView()
        await interaction.response.send_message("Manager Menu", view=view)
        await view.wait()

        # TODO: add choices to set min players, set week's schedule, schedule release time
        while view.choice != -1:
            if view.choice == 0:
                await interaction.delete_original_response()
                interaction = await self.send_set_team_times_view(
                    view.interaction, team_id
                )
            view = ManagerMenuView()
            await interaction.edit_original_response(view=view)
            await view.wait()

        return view.interaction

    # takes fresh interaction
    async def send_set_team_times_view(self, interaction: discord.Interaction, team_id):
        string_schedule = self.db.get_team_scrim_blocks(team_id)
        if string_schedule:
            # pyright doesn't trust the power of the pickle
            schedule: Schedule = unpickle(string_schedule)
        else:
            schedule = Schedule([], [], [], [], [], [], [])

        interaction = await self.send_day_selection_view(interaction, schedule)
        pickled_schedule = pickle(schedule)
        self.db.set_team_scrim_blocks(team_id, pickled_schedule)
        return interaction

    # takes fresh interaction
    async def send_day_selection_view(
        self, interaction: discord.Interaction, schedule: Schedule
    ):
        view = SelectDayView(interaction, confirmed_disabled=True)
        await interaction.response.send_message("Select Day", view=view)
        await view.wait()
        selections: list[int]
        while view.choice != -1:
            if view.choice == 0:
                await view.interaction.response.defer()
                day_name = SCRIM_DAYS[selections[0]]
                interaction, times = await self.send_time_selection_view(interaction)
                setattr(schedule, day_name, times)
                view = SelectDayView(interaction, confirmed_disabled=False)
                await interaction.response.send_message("Select Day", view=view)
            else:
                selections = view.selections
                view = SelectDayView(interaction, confirmed_disabled=False)
                await interaction.edit_original_response(
                    content=SCRIM_DAYS[selections[0]].capitalize(), view=view
                )
            await view.wait()

        return view.interaction

    # takes responded to interaction
    async def send_time_selection_view(self, interaction: discord.Interaction):
        view = SelectTimesView(interaction, confirmed_disabled=True)
        times = []
        await interaction.edit_original_response(content="Set Times", view=view)
        await view.wait()
        while view.choice != -1 and view.choice != 0:
            # set times to selections
            times = view.selections
            # reset view
            view = SelectTimesView(interaction, confirmed_disabled=False)
            content = ""
            for time in times:
                content += SCRIM_TIMES[time] + "\n"
            # edit response with selections and new view
            await interaction.edit_original_response(content=content, view=view)
            # wait for response
            await view.wait()
        return view.interaction, times

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


class SelectDayView(ResponseSelectView):
    def __init__(self, interaction, confirmed_disabled):
        super().__init__(interaction, confirmed_disabled)
        schedule = Schedule([], [], [], [], [], [], [])
        select_items = []
        for key, value in SCRIM_DAYS.items():
            select_items.append(ResponseOption(value.capitalize(), key))
        self.add_item(ResponseSelect(select_items, 0, max_values=1))


class SelectTimesView(ResponseSelectView):
    def __init__(self, interaction, confirmed_disabled):
        super().__init__(interaction, confirmed_disabled)
        select_items = []
        for keys, values in SCRIM_TIMES.items():
            select_items.append(ResponseOption(values, keys))
        self.add_item(ResponseSelect(select_items, 0))


async def setup(bot):
    await bot.add_cog(Scheduler(bot))
