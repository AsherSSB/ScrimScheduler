import discord
import discord.ui as ui
import asyncio


class DiscordResponsiveUI():
    def __init__(self):
        pass

    async def send_responsive_modal(self, interaction:discord.Interaction, title, *fields):
        modal = ResponseModal(interaction, title, fields)
        await modal.view.wait()
        return modal.responses


class ResponseView(ui.View):
    def __init__(self):
        super().__init__()
        self.interaction: discord.Interaction
        self.choice = -999
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


class ResponseOption(discord.SelectOption):
    def __init__(self, label: str, value: int, emoji=None):
        super().__init__(label=label, value=value, emoji=emoji)


class ResponseSelect(ui.Select):
    def __init__(self, options: list[ResponseOption], row=None):
        super().__init__(options=options, max_values=len(options), row=row)

    async def callback(self, interaction):
        self.view.interaction = interaction
        self.view.choice = [int(value) for value in self.values]
        self.view.event.set()


class SingleTextSubmission(ui.Modal):
    def __init__(self, title, label):
        super().__init__(title=title)
        self.interaction: discord.Interaction
        self.input = ui.TextInput(label=label, required=True)
        self.add_item(self.textinput)
        self.event = asyncio.Event()

    async def on_submit(self, interaction:discord.Interaction): 
        self.interaction = interaction
        self.event.set()

    async def wait(self):
        await self.event.wait()


class DoubleTextSubmission(ui.Modal):
    def __init__(self, title, label1, label2):
        super().__init__(title=title)
        self.interaction: discord.Interaction
        self.first_input = ui.TextInput(label=label1, required=True)
        self.second_input = ui.TextInput(label=label2, required=True)
        self.add_item(self.first_input)
        self.add_item(self.second_input)
        self.event = asyncio.Event()

    async def on_submit(self, interaction:discord.Interaction):
        self.interaction = interaction
        self.event.set()

    async def wait(self):
        await self.event.wait()


class ConfirmView(ResponseView):
    def __init__(self):
        self.add_item(ResponseButton("Confirm", 0, style=discord.ButtonStyle.green, emoji="✅", row=0))
        self.add_item(ResponseButton("Cancel", -1, style=discord.ButtonStyle.red, emoji="❌", row=0))


class ResponseModalHandler():
    def __init__(self, title, old_interaction, fresh_interaction, *fields):
        self.view_interaction = old_interaction
        self.modal_interaction = fresh_interaction
        self.modal_title = title
        self.fields = fields
        self.event = asyncio.Event()
        self.setter = ""
        self.view: ModalView
        self.modal: ResponseModal

    async def loop_view(self):
        # create modal
        self.modal = ResponseModal(self.modal_title, self.modal_interaction, self, self.fields)
        # create and send view
        self.view = ModalView()
        # send modal
        # wait for event
        # if setter is view
        # if view choice is 0
        # reset event
        # recurse
        # else
        # return
        pass

    async def send_response_modal(self):
        # send looped view
        # if responses
        # return interaction, responses
        # else:
        # return interaction, None
        pass

    async def wait(self):
        await self.event.wait()


class ResendModalButton(ui.Button):
    def __init__(self):
        super().__init__(label="Resend Modal", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        modal = ResponseModal(self.view.handler.modal_title, self.view.handler, self.view.handler.fields)
        self.view.handler.modal = modal
        await self.view.interaction.edit_original_response("Answer Modal")
        await interaction.response.send_modal(self.view.modal)


class ModalView(ui.View):
    def __init__(self, interaction, handler):
        super().__init__()
        self.interaction: discord.interaction = interaction
        self.handler = handler


class ResponseModal(ui.Modal):
    def __init__(self, title, handler, *fields):
        super().__init__(title=title)
        self.handler = handler
        self.text_inputs = []
        self.responses = {}
        for field in fields:
            self.text_inputs.append(ui.TextInput(label=field, required=True))

    async def on_submit(self, interaction: discord.Interaction):
        self.hander.interaction = interaction
        self.handler.event.set()
