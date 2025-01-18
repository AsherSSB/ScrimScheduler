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
    def __init__(self, label, choice, style=discord.ButtonStyle.blurple, emoji=None):
        super().__init__(label=label, style=style, emoji=emoji)
        self.choice = choice

    async def callback(self, interaction):
        self.view.interaction = interaction
        self.view.choice = self.choice
        self.view.event.set()

