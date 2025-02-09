import discord
import discord.ui as ui
import asyncio


class DiscordResponsiveUI:
    def __init__(self):
        pass

    async def send_responsive_modal(
        self, old_interaction, fresh_interaction: discord.Interaction, title, *fields
    ):
        handler = ResponseModalHandler(
            title, old_interaction, fresh_interaction, fields
        )
        interaction, response_dict = await handler.send_response_modal()
        return interaction, response_dict


class ResponseView(ui.View):
    def __init__(self):
        super().__init__()
        self.interaction: discord.Interaction
        self.choice = -999
        self.event = asyncio.Event()

    async def wait(self):
        await self.event.wait()


class ResponseButton(ui.Button):
    def __init__(
        self, label, choice, style=discord.ButtonStyle.blurple, emoji=None, row=None
    ):
        super().__init__(label=label, style=style, emoji=emoji, row=row)
        self.choice = choice
        self.view: ResponseView

    async def callback(self, interaction):
        self.view.interaction = interaction
        self.view.choice = self.choice
        self.view.event.set()


class ResponseSelectView(ResponseView):
    def __init__(self, interaction, confirmed_disabled):
        super().__init__()
        self.choice = -99
        self.selections = []
        self.add_item(ResponseButton("back", -1, discord.ButtonStyle.red, row=4))
        self.confirm_button = ResponseButton(
            "Confirm Changes", 0, discord.ButtonStyle.green, row=4
        )
        self.confirm_button.disabled = confirmed_disabled
        self.add_item(self.confirm_button)
        self.interaction: discord.Interaction = interaction


class ResponseOption(discord.SelectOption):
    def __init__(self, label: str, value: int, emoji=None):
        super().__init__(label=label, value=str(value), emoji=emoji)


class ResponseSelect(ui.Select):
    def __init__(self, options: list[discord.SelectOption], row=None, max_values=None):
        if not max_values:
            max_values = len(options)
        super().__init__(options=options, max_values=max_values, row=row)
        self.view: ResponseSelectView

    async def callback(self, interaction):
        await interaction.response.defer()
        self.view.selections = [int(value) for value in self.values]
        self.view.event.set()


class SingleTextSubmission(ui.Modal):
    def __init__(self, title, label):
        super().__init__(title=title)
        self.interaction: discord.Interaction
        self.text_input = ui.TextInput(label=label, required=True)
        self.add_item(self.text_input)
        self.event = asyncio.Event()

    async def on_submit(self, interaction: discord.Interaction):
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

    async def on_submit(self, interaction: discord.Interaction):
        self.interaction = interaction
        self.event.set()

    async def wait(self):
        await self.event.wait()


class ConfirmView(ResponseView):
    def __init__(self):
        self.add_item(
            ResponseButton(
                "Confirm", 0, style=discord.ButtonStyle.green, emoji="✅", row=0
            )
        )
        self.add_item(
            ResponseButton(
                "Cancel", -1, style=discord.ButtonStyle.red, emoji="❌", row=0
            )
        )


class ResponseModalHandler:
    def __init__(self, title, old_interaction, fresh_interaction, *fields):
        self.view_interaction = old_interaction
        self.modal_interaction = fresh_interaction
        self.modal_title = title
        self.fields = fields
        self.event = asyncio.Event()
        self.setter = ""
        self.view: ModalView
        self.modal: ResponseModal

    async def send_response_modal(self) -> tuple:
        # create modal
        self.modal = ResponseModal(self)
        # create and send view
        self.view = ModalView(self)
        await self.view_interaction.edit_original_response(
            content="Modal Menu", view=self.view
        )
        # send modal
        await self.modal_interaction.response.send_modal(self.modal)
        # wait for event
        await self.event.wait()
        # if setter is view
        if self.setter == "view":
            self.modal_interaction = self.view.interaction
            # if view choice is 0
            if self.view.choice == 0:
                self.event = asyncio.Event()
                interaction, responses = await self.send_response_modal()
                return interaction, responses
            else:
                return self.modal_interaction, {}
        else:
            return self.modal.interaction, self.modal.responses


class ModalView(ui.View):
    def __init__(self, handler):
        super().__init__()
        self.handler = handler
        self.interaction: discord.Interaction
        self.choice: int

    @ui.button(label="Resend Modal", style=discord.ButtonStyle.green)
    async def resend_modal_button(self, interaction: discord.Interaction, button):
        self.choice = 0
        self.interaction = interaction
        self.handler.setter = "view"
        self.handler.event.set()

    @ui.button(label="Back", style=discord.ButtonStyle.red)
    async def back_button(self, interaction: discord.Interaction, button):
        self.choice = -1
        self.interaction = interaction
        self.handler.setter = "view"
        self.handler.event.set()


class ResponseModal(ui.Modal):
    def __init__(self, handler: ResponseModalHandler):
        super().__init__(title=handler.modal_title)
        self.handler = handler
        self.responses = {}

        if not (1 <= len(self.handler.fields) <= 5):
            raise ValueError("ResponseModal only takes between 1 and 5 args")

        for field in handler.fields:
            text_input = ui.TextInput(
                label=field,
                style=discord.TextStyle.short,
                required=True,
            )
            self.add_item(text_input)
            self.responses[field] = text_input

        self.interaction: discord.Interaction

    async def on_submit(self, interaction: discord.Interaction):
        self.responses = {label: field.value for label, field in self.responses.items()}
        self.interaction = interaction
        self.handler.setter = "modal"
        self.handler.event.set()
