import discord
import discord.ui as ui
import asyncio


class ResponseView(ui.View):
    def __init__(self):
        super().__init__()
        self.interaction: discord.Interaction
        self.choice
        self.event = asyncio.Event()

    async def wait(self):
        await self.event.wait()


class ResponseButton(ui.Button):
    def __init__(self, label, choice, style=discord.ButtonStyle.blurple, emoji=None, row=None):
        super().__init__(label=label, style=style, emoji=emoji, row=row)
        self.choice = choice

    async def callback(self, interaction):
        self.view.interaction = interaction
        self.view.choice = self.choice
        self.view.event.set()


class ResponseOption(ui.SelectOption):
    def __init__(self, label: str, value: int, emoji=None):
        super().__init__(label=label, value=value, emoji=emoji)


class ResponseSelect(ui.Select):
    def __init__(self, options: list[ResponseOption], row=None):
        super().__init__(options=options, max_values=len(options), row=row)

    async def callback(self, interaction):
        self.view.interaction = interaction
        self.view.choice = [int(value) for value in self.values]
        self.view.event.set()


class SingleTextSubmission(discord.ui.Modal):
    def __init__(self, title, label):
        super().__init__(title=title)
        self.input = discord.ui.TextInput(label=label, required=True)
        self.add_item(self.textinput)
        self.event = asyncio.Event()

    async def on_submit(self, interaction:discord.Interaction):
        await interaction.response.defer()
        self.event.set()

    async def wait(self):
        await self.event.wait()


class DoubleTextSubmission(discord.ui.Modal):
    def __init__(self, title, label1, label2):
        super().__init__(title=title)
        self.first_input = discord.ui.TextInput(label=label1, required=True)
        self.second_input = discord.ui.TextInput(label=label2, required=True)
        self.add_item(self.first_input)
        self.add_item(self.second_input)
        self.event = asyncio.Event()

    async def on_submit(self, interaction:discord.Interaction):
        await interaction.response.defer()
        self.event.set()

    async def wait(self):
        await self.event.wait()


