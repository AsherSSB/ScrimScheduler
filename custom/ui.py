import discord
import discord.ui as ui
import asyncio


class ResponseView(ui.View):
    def __init__(self):
        super().__init__()
        self.choice: int
        self.interaction: discord.Interaction
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

