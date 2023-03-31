from datetime import datetime, timedelta
from dataclasses import dataclass
import disnake
from disnake import TextInputStyle
from disnake.ext import commands, tasks

from typing import TYPE_CHECKING

import constants

if TYPE_CHECKING:
    from bot import Monodrone

DELETE_ROLES = (
    516369428615528459,   # DDB Staff
    516370028053004306,   # Moderator
    # 1064918245989175438,  # Test Server Moderator
)

CHANNELS = {
    # "Dungeon Master": 1060611482783584266,  # Test Server
    # "Players": 1064888625688494090,
    # "Community": 1064888696039542854,
    # "Paid": 1064888713311694878,

    "Dungeon Master": 750812887697588356,  # D&D Server
    "Players": 750813601358676008,
    "Community": 880956314308714566,
    "Paid": 880958115363840041,
}

# data schema:
# lookingforgroup.json: dict int->list[int, int] author_id->list[cooldown, message_id]


@dataclass
class LookingForField:
    value: str
    desc: str
    placeholder: str = None
    style: TextInputStyle = None

    def __post_init__(self):
        if self.placeholder is None:
            self.placeholder = self.desc
        if self.style is None:
            self.style = TextInputStyle.short


looking_for_dm = {
    "experience": LookingForField(
        value="[1] Player Experience",
        desc="Are you brand new, played a few years, a long time player?"
    ),
    "time": LookingForField(
        value="[2] Location/Timezone",
        desc=(
            "Your region and/or timezone as appropriate. You can use [Discord"
            " timestamp](https://hammertime.cyou/) tags here!"
        ),
        placeholder="Your region and/or timezone as appropriate.",
    ),
    "availability": LookingForField(value="[3] Availability", desc="Describe when you are available to play."),
    "style": LookingForField(
        value="[4] Game Style",
        desc=(
            "Some information about what sort of game you are looking (e.g. roleplay heavy, hack'n'slash, political "
            "intrigue, horror, etc.). This could include what edition of D&D you play, or how you feel about homebrew!"
        ),
        placeholder="What sort of game are you looking for?",
    ),
    "method": LookingForField(
        value="[5] Preferred Way to Play",
        desc=(
            "How would you like to play? Video over a specific chat service? Text only? Play by post? Using "
            "Discord/DDB/A specific VTT system?"
        ),
        placeholder="How would you like to play?",
    ),
    "opt_in": LookingForField(
        value="[6] Opt In (Default: Opt Out to All)",
        desc=(
            "If you would like to receive invites from Community Games, Paid Games, or other similar services "
            "please indicate that here"
        ),
    ),
    "additional": LookingForField(
        value="[7] Additional Information (Optional)",
        desc=(
            "Any additional information you think it’s important for prospective groups to know about. Try to keep "
            "this clear and concise."
        ),
        placeholder="Any extra information you think it’s important for prospective groups to know about.",
        style=TextInputStyle.paragraph,
    ),
}

looking_for_players = {
    "time": LookingForField(
        value="[1] Game Time",
        desc="Time and date, including timezone. You can use [Discord timestamp](https://hammertime.cyou/) tags here!",
        placeholder="Time and date, including timezone.",
    ),
    "style": LookingForField(
        value="[2] What style of game does the group play?",
        desc="Eg. Roleplay heavy, hack and slash, political intrigue, horror, official adventure, homebrew, etc. "
             "This could include what edition of D&D you play, or how you feel about homebrew!",
        placeholder="What sort of game are you looking for?",
    ),
    "method": LookingForField(
        value="[3] How does your group play?",
        desc=(
            "Video over a specific chat service? Text only? Play by post? Using Discord/DDB/A specific VTT system? Eg."
            " Video, voice, VTT, etc."
        ),
        placeholder="Eg. Video, voice, VTT, etc.",
    ),
    "spaces": LookingForField(
        value="[4] Number of available spaces.",
        desc="How many people are you looking for?",
    ),
    "additional": LookingForField(
        value="[5] Additional Information (Optional)",
        desc=(
            "Any additional information you think it’s important for prospective players to know about. Try to keep "
            "this clear and concise."
        ),
        placeholder="Any extra information you think it’s important for prospective players to know about.",
        style=TextInputStyle.paragraph,
    ),
}

looking_for_paid = {
    "time": LookingForField(
        value="[1] Game Time",
        desc=(
            "Describe the time slot(s) you have available. You can use [Discord timestamp](https://hammertime.cyou/)"
            " tags here!"
        ),
        placeholder="Describe the time slot(s) you have available.",
    ),
    "style": LookingForField(
        value="[2] What style of game does the group play?",
        desc="Eg. Roleplay heavy, hack and slash, political intrigue, horror, official adventure, homebrew, etc. "
             "This could include what edition of D&D you play, or how you feel about homebrew!",
        placeholder="What sort of game are you looking for?",
    ),
    "method": LookingForField(
        value="[3] How does your group play?",
        desc="Video over a specific chat service? Text only? Play by post? Using Discord/DDB/A specific VTT system?",
        placeholder="Eg. Video, voice, VTT, etc.",
    ),
    "spaces": LookingForField(
        value="[4] Number of available spaces.",
        desc="How many people are you looking for?",
    ),
    "rate": LookingForField(value="[5] Rate", desc="What is the cost for your services?"),
    "additional": LookingForField(
        value="[6] Additional Information (Optional)",
        desc=(
            "Any additional information you think it’s important for prospective players to know about. Try to keep "
            "this clear and concise."
        ),
        placeholder="Any extra information you think it’s important for prospective players to know about.",
        style=TextInputStyle.paragraph,
    ),
}

looking_for_community = {
    "name": LookingForField(value="[1] Community Name", desc="The name of your commmunity"),
    "style": LookingForField(
        value="[2] Game Style(s)",
        desc=(
            "Some information about what sort of games your community focuses on (eg. roleplay heavy, hack'n'slash,"
            " political intrigue, etc.)"
        ),
        placeholder="What sort of game(s) does your community play?",
    ),
    "methods": LookingForField(
        value="[3] Way(s) we play",
        desc=(
            "How does your community play? Video over a specific chat service? Text? Play by post? Using Discord/DDB/A"
            " specific VTT system? This could include what edition of D&D you play, or how you feel about homebrew!"
        ),
        placeholder="How does your community play?",
    ),
    "link": LookingForField(value="[4] Discord Link", desc="The link to your Discord Community"),
    "additional": LookingForField(
        value="[5] Additional Information (Optional)",
        desc=(
            "Any additional information you think it’s important for prospective players to know about. Try to keep "
            "this clear and concise."
        ),
        placeholder="Any extra information you think it’s important for prospective players to know about.",
        style=TextInputStyle.paragraph,
    ),
}

opt_in_options = [
    disnake.SelectOption(
        label="Community Games",
        description="For example: West Marches, or multi-campaign servers",
        value="invite",
    ),
    disnake.SelectOption(
        label="Paid Games",
        description="Are you open towards paid DMing services?",
        value="paid",
    ),
    disnake.SelectOption(
        label="Other Services",
        description="Are you interested in other types of servers/services?",
        value="other",
    ),
]


class SubmissionView(disnake.ui.View):
    def __init__(self, bot: "Monodrone" = None, lf_type: str = None, lfg_timers: dict = None):
        super().__init__(timeout=None)
        self.bot = bot
        self.lf_type = lf_type
        self.lfg_timers = lfg_timers
        if self.lfg_timers is None:
            self.lfg_timers = self.bot.db.jget("lookingforgroup", {})

    @disnake.ui.button(
        label="Cancel",
        style=disnake.ButtonStyle.danger,
        row=4,
    )
    async def cancel(self, _: disnake.ui.Button, inter: disnake.Interaction):
        await inter.response.defer()
        await inter.edit_original_message(embed=None, view=None, content="Submission cancelled.")

    @disnake.ui.button(
        label="Submit",
        style=disnake.ButtonStyle.success,
        row=4,
        disabled=True,
    )
    async def submit(self, _: disnake.ui.Button, inter: disnake.Interaction):
        await inter.response.defer()
        message = await inter.original_message()
        embed = message.embeds[0]

        for index, field in enumerate(embed.fields):
            value = field.value.splitlines()[1:]
            if not value:
                embed.remove_field(index)
                continue
            embed.set_field_at(index=index, name=field.name, value="\n".join(value), inline=False)

        embed.description = None

        channel = self.bot.get_channel(CHANNELS.get(self.lf_type))
        submission = await channel.send(
            content=f"{inter.author.mention}",
            embed=embed,
            view=PostedView(self.bot, lfg_timers=self.lfg_timers),
        )

        await submission.create_thread(
            name=f"{inter.author} - Looking for {self.lf_type}",
            auto_archive_duration=10080,
        )
        await inter.edit_original_message(
            embed=None,
            view=None,
            content=f"Form submitted! [View it here]({submission.jump_url})",
        )

        # set timer
        if str(inter.author.id) not in self.lfg_timers:
            self.lfg_timers[str(inter.author.id)] = {}
        self.lfg_timers[str(inter.author.id)][self.lf_type] = (
            int(embed.timestamp.timestamp()),
            submission.id,
        )

        self.bot.db.jset("lookingforgroup", self.lfg_timers)


class ModResetView(disnake.ui.View):
    def __init__(
        self,
        bot: "Monodrone" = None,
        lf_type: str = None,
        lfg_timers: dict = None,
        target: disnake.Member = None,
    ):
        super().__init__(timeout=None)
        self.bot = bot
        self.lf_type = lf_type
        self.lfg_timers = lfg_timers
        self.target = target
        if self.lfg_timers is None:
            self.lfg_timers = self.bot.db.jget("lookingforgroup", {})

    @disnake.ui.button(
        label="Reset Timer",
        style=disnake.ButtonStyle.blurple,
        custom_id="persistent:reset",
    )
    async def reset(self, _: disnake.ui.Button, inter: disnake.Interaction):
        await inter.response.defer()

        # remove timer
        if str(self.target.id) in self.lfg_timers:
            self.lfg_timers[str(self.target.id)].pop(self.lf_type, None)

        self.bot.db.jset("lookingforgroup", self.lfg_timers)
        await inter.edit_original_message(view=None, content=f"{self.lf_type} timer reset for {self.target.mention}")

        log_channel = self.bot.get_channel(constants.OUTPUT_CHANNEL_ID)
        await log_channel.send(f"{inter.author.mention} reset {self.target.mention}'s {self.lf_type} timer.")


class PostedView(disnake.ui.View):
    def __init__(self, bot: "Monodrone" = None, lfg_timers: dict = None):
        super().__init__(timeout=None)
        self.bot = bot
        self.lfg_timers = lfg_timers
        self.last_pressed = 0
        if self.lfg_timers is None:
            self.lfg_timers = self.bot.db.jget("lookingforgroup", {})

    @disnake.ui.button(
        label="Delete",
        style=disnake.ButtonStyle.danger,
        row=4,
        custom_id="persistent:delete",
    )
    async def delete(self, _: disnake.ui.Button, inter: disnake.Interaction):
        await inter.response.defer()

        message = await inter.original_message()
        embed = message.embeds[0]
        timestamp = int(embed.timestamp.timestamp())
        original_author = await inter.guild.fetch_member(int(embed.footer.text[9:-13]))

        lf_type = None
        match embed.title:
            case "Player Looking for Dungeon Master":
                lf_type = "Dungeon Master"
            case "Dungeon Master Looking for Players":
                lf_type = "Players"
            case "Looking for Community":
                lf_type = "Community"
            case "Paid Dungeon Master Looking for Players":
                lf_type = "Paid"

        # if not the original author of the submission, or staff, ignore
        if not (inter.author == original_author or set(r.id for r in inter.author.roles).intersection(DELETE_ROLES)):
            return

        if not self.last_pressed or (datetime.now().timestamp() - self.last_pressed) > 10:
            self.last_pressed = datetime.now().timestamp()
            await inter.send(f"Remember you won’t be able to submit another {embed.title} until <t:{timestamp}> "
                             f"(<t:{timestamp}:R>), even after deleting. If you have errors in your post, please "
                             f"utilize the thread that was created to correct or clarify.\n\nPress delete again within "
                             f"the next 10 second to confirm.",
                             ephemeral=True)
            return

        if inter.author == original_author:
            view = disnake.utils.MISSING
            pronoun = "You"
        else:
            view = ModResetView(
                bot=self.bot,
                lf_type=lf_type,
                lfg_timers=self.lfg_timers,
                target=original_author,
            )
            pronoun = "They"

        log_channel = self.bot.get_channel(constants.OUTPUT_CHANNEL_ID)
        await log_channel.send(f"{inter.author.mention} deleted {original_author.mention}'s {embed.title} submission:",
                               embed=embed)
        await inter.delete_original_message()

        await inter.send(
            f"Submission removed. {pronoun} can post another on: <t:{timestamp}> (<t:{timestamp}:R>)",
            ephemeral=True,
            view=view,
        )


class DMSubmissionView(SubmissionView):
    def __init__(self, bot=None, lf_type="Dungeon Master", lfg_timers=None):
        super().__init__(bot=bot, lf_type=lf_type, lfg_timers=lfg_timers)
        self.components = [
            disnake.ui.TextInput(
                label=looking_for_dm[comp_type].value,
                placeholder=looking_for_dm[comp_type].placeholder,
                custom_id=comp_type,
                style=looking_for_dm[comp_type].style,
                max_length=750,
            )
            for comp_type in looking_for_dm
            if not comp_type.startswith("opt_")
        ]

    @disnake.ui.button(
        label="Edit Responses [1-5]",
        custom_id="dm_edit_1-5",
        style=disnake.ButtonStyle.blurple,
    )
    async def edit_1_5_button(self, _: disnake.ui.Button, inter: disnake.Interaction):
        randomized_id = f"looking-for-dm-{inter.id}_0"

        modal = SubmissionModal(
            title="Looking for DM",
            custom_id=randomized_id,
            components=self.components[:5],
        )
        await inter.response.send_modal(modal=modal)
        modal_inter = await self.bot.wait_for(
            "modal_submit",
            check=lambda modal_inter: modal_inter.custom_id == randomized_id and modal_inter.author == inter.author,
        )
        embed = (await inter.original_message()).embeds[0]
        values = modal_inter.text_values
        for index, (name, value) in enumerate(values.items()):
            if not value:
                continue
            embed.set_field_at(
                index=index,
                name=looking_for_dm[name].value,
                value=f"> {looking_for_dm[name].desc}\n {value}",
                inline=False,
            )

        self.submit.disabled = False
        await inter.edit_original_message(embed=embed, view=self)

    @disnake.ui.button(
        label="Edit Responses [7]",
        custom_id="dm_edit_7",
        style=disnake.ButtonStyle.blurple,
    )
    async def edit_7_button(self, _: disnake.ui.Button, inter: disnake.Interaction):
        randomized_id = f"looking-for-dm-{inter.id}_1"
        modal = SubmissionModal(
            title="Looking for DM",
            custom_id=randomized_id,
            components=self.components[5:6],
        )
        await inter.response.send_modal(modal=modal)
        modal_inter = await self.bot.wait_for(
            "modal_submit",
            check=lambda modal_inter: modal_inter.custom_id == randomized_id and modal_inter.author == inter.author,
        )

        embed = (await inter.original_message()).embeds[0]
        embed.set_field_at(
            index=6,
            name=looking_for_dm["additional"].value,
            value=f"> {looking_for_dm['additional'].desc}\n {modal_inter.text_values['additional']}",
            inline=False,
        )

        await inter.edit_original_message(embed=embed, view=self)

    @disnake.ui.select(
        placeholder="Opt-In Options",
        options=opt_in_options,
        max_values=3,
        custom_id="dm_opt_in",
    )
    async def opt_in_select(self, select: disnake.ui.Select, inter: disnake.Interaction):
        def opt_in(option):
            return "✅" if option in select.values else "❌"

        await inter.response.defer()
        embed = (await inter.original_message()).embeds[0]
        embed.set_field_at(
            index=5,
            name=looking_for_dm["opt_in"].value,
            value=(
                f"{looking_for_dm['opt_in'].desc}\n {opt_in('invite')} Community Games\n"
                f"{opt_in('paid')} Paid Games\n{opt_in('other')} Other Services"
            ),
            inline=False,
        )

        await inter.edit_original_message(embed=embed, view=self)


class PlayersSubmissionView(SubmissionView):
    def __init__(self, bot=None, lf_type="Players", lfg_timers=None):
        super().__init__(bot=bot, lf_type=lf_type, lfg_timers=lfg_timers)
        self.components = [
            disnake.ui.TextInput(
                label=looking_for_players[comp_type].value,
                placeholder=looking_for_players[comp_type].placeholder,
                custom_id=comp_type,
                style=looking_for_players[comp_type].style,
                max_length=750,
            )
            for comp_type in looking_for_players
        ]

    @disnake.ui.button(
        label="Edit Responses [1-4]",
        custom_id="players_edit_1-4",
        style=disnake.ButtonStyle.blurple,
    )
    async def edit_1_4_button(self, _: disnake.ui.Button, inter: disnake.Interaction):
        randomized_id = f"looking-for-players-{inter.id}_0"

        modal = SubmissionModal(
            title="Looking for Players",
            custom_id=randomized_id,
            components=self.components[:4],
        )
        await inter.response.send_modal(modal=modal)
        modal_inter = await self.bot.wait_for(
            "modal_submit",
            check=lambda modal_inter: modal_inter.custom_id == randomized_id and modal_inter.author == inter.author,
        )
        embed = (await inter.original_message()).embeds[0]
        values = modal_inter.text_values
        for index, (name, value) in enumerate(values.items()):
            if not value:
                continue
            embed.set_field_at(
                index=index,
                name=looking_for_players[name].value,
                value=f"> {looking_for_players[name].desc}\n {value}",
                inline=False,
            )

        self.submit.disabled = False
        await inter.edit_original_message(embed=embed, view=self)

    @disnake.ui.button(
        label="Edit Responses [5]",
        custom_id="players_edit_5",
        style=disnake.ButtonStyle.blurple,
    )
    async def edit_5_button(self, _: disnake.ui.Button, inter: disnake.Interaction):
        randomized_id = f"looking-for-players-{inter.id}_1"
        modal = SubmissionModal(
            title="Looking for Players",
            custom_id=randomized_id,
            components=self.components[4:5],
        )
        await inter.response.send_modal(modal=modal)
        modal_inter = await self.bot.wait_for(
            "modal_submit",
            check=lambda modal_inter: modal_inter.custom_id == randomized_id and modal_inter.author == inter.author,
        )

        embed = (await inter.original_message()).embeds[0]
        embed.set_field_at(
            index=4,
            name=looking_for_players["additional"].value,
            value=f"> {looking_for_players['additional'].desc}\n {modal_inter.text_values['additional']}",
            inline=False,
        )

        await inter.edit_original_message(embed=embed, view=self)


class CommunitySubmissionView(SubmissionView):
    def __init__(self, bot=None, lf_type="Community", lfg_timers=None):
        super().__init__(bot=bot, lf_type=lf_type, lfg_timers=lfg_timers)
        self.components = [
            disnake.ui.TextInput(
                label=looking_for_community[comp_type].value,
                placeholder=looking_for_community[comp_type].placeholder,
                custom_id=comp_type,
                style=looking_for_community[comp_type].style,
                max_length=750,
            )
            for comp_type in looking_for_community
        ]

    @disnake.ui.button(
        label="Edit Responses [1-4]",
        custom_id="community_edit_1-4",
        style=disnake.ButtonStyle.blurple,
    )
    async def edit_1_4_button(self, _: disnake.ui.Button, inter: disnake.Interaction):
        randomized_id = f"looking-for-community-{inter.id}_0"

        modal = SubmissionModal(
            title="Looking for Community",
            custom_id=randomized_id,
            components=self.components[:4],
        )
        await inter.response.send_modal(modal=modal)
        modal_inter = await self.bot.wait_for(
            "modal_submit",
            check=lambda modal_inter: modal_inter.custom_id == randomized_id and modal_inter.author == inter.author,
        )
        embed = (await inter.original_message()).embeds[0]
        values = modal_inter.text_values
        for index, (name, value) in enumerate(values.items()):
            if not value:
                continue
            embed.set_field_at(
                index=index,
                name=looking_for_community[name].value,
                value=f"> {looking_for_community[name].desc}\n {value}",
                inline=False,
            )

        self.submit.disabled = False
        await inter.edit_original_message(embed=embed, view=self)

    @disnake.ui.button(
        label="Edit Responses [5]",
        custom_id="community_edit_5",
        style=disnake.ButtonStyle.blurple,
    )
    async def edit_7_button(self, _: disnake.ui.Button, inter: disnake.Interaction):
        randomized_id = f"looking-for-community-{inter.id}_1"
        modal = SubmissionModal(
            title="Looking for Community",
            custom_id=randomized_id,
            components=self.components[4:5],
        )
        await inter.response.send_modal(modal=modal)
        modal_inter = await self.bot.wait_for(
            "modal_submit",
            check=lambda modal_inter: modal_inter.custom_id == randomized_id and modal_inter.author == inter.author,
        )

        embed = (await inter.original_message()).embeds[0]
        embed.set_field_at(
            index=4,
            name=looking_for_community["additional"].value,
            value=f"> {looking_for_community['additional'].desc}\n {modal_inter.text_values['additional']}",
            inline=False,
        )

        await inter.edit_original_message(embed=embed, view=self)


class PaidSubmissionView(SubmissionView):
    def __init__(self, bot=None, lf_type="Paid", lfg_timers=None):
        super().__init__(bot=bot, lf_type=lf_type, lfg_timers=lfg_timers)
        self.components = [
            disnake.ui.TextInput(
                label=looking_for_paid[comp_type].value,
                placeholder=looking_for_paid[comp_type].placeholder,
                custom_id=comp_type,
                style=looking_for_paid[comp_type].style,
                max_length=750,
            )
            for comp_type in looking_for_paid
        ]

    @disnake.ui.button(
        label="Edit Responses [1-5]",
        custom_id="paid_edit_1-5",
        style=disnake.ButtonStyle.blurple,
    )
    async def edit_1_5_button(self, _: disnake.ui.Button, inter: disnake.Interaction):
        randomized_id = f"looking-for-paid-dm-{inter.id}_0"

        modal = SubmissionModal(
            title="Looking for Paid DM",
            custom_id=randomized_id,
            components=self.components[:5],
        )
        await inter.response.send_modal(modal=modal)
        modal_inter = await self.bot.wait_for(
            "modal_submit",
            check=lambda modal_inter: modal_inter.custom_id == randomized_id and modal_inter.author == inter.author,
        )
        embed = (await inter.original_message()).embeds[0]
        values = modal_inter.text_values
        for index, (name, value) in enumerate(values.items()):
            if not value:
                continue
            embed.set_field_at(
                index=index,
                name=looking_for_paid[name].value,
                value=f"> {looking_for_paid[name].desc}\n {value}",
                inline=False,
            )

        self.submit.disabled = False
        await inter.edit_original_message(embed=embed, view=self)

    @disnake.ui.button(
        label="Edit Responses [6]",
        custom_id="paid_edit_6",
        style=disnake.ButtonStyle.blurple,
    )
    async def edit_5_button(self, _: disnake.ui.Button, inter: disnake.Interaction):
        randomized_id = f"looking-for-paid-dm-{inter.id}_1"
        modal = SubmissionModal(
            title="Looking for Paid DM",
            custom_id=randomized_id,
            components=self.components[5:6],
        )
        await inter.response.send_modal(modal=modal)
        modal_inter = await self.bot.wait_for(
            "modal_submit",
            check=lambda modal_inter: modal_inter.custom_id == randomized_id and modal_inter.author == inter.author,
        )

        embed = (await inter.original_message()).embeds[0]
        embed.set_field_at(
            index=5,
            name=looking_for_paid["additional"].value,
            value=f"> {looking_for_paid['additional'].desc}\n {modal_inter.text_values['additional']}",
            inline=False,
        )

        await inter.edit_original_message(embed=embed, view=self)


class SubmissionModal(disnake.ui.Modal):
    def __init__(self, title, custom_id, components: list[disnake.ui.TextInput]):
        super().__init__(title=title, components=components, custom_id=custom_id)

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        await inter.response.defer(with_message=False)

    async def on_error(self, error: Exception, inter: disnake.ModalInteraction) -> None:
        await inter.response.send_message("Oops, something went wrong.", ephemeral=True)


class LookingForGroup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop_offset = datetime.now()
        self.lfg_timers = bot.db.jget("lookingforgroup", {})

    def cog_load(self):
        self.bot.add_view(PostedView(bot=self.bot, lfg_timers=self.lfg_timers))

        self.cleanup_timers.start()

        self.get_loop_offset()

    def cog_unload(self):
        self.cleanup_timers.cancel()

    def get_loop_offset(self):
        # Try to get the autodelete loop timing
        auto_delete_cog = self.bot.get_cog("AutoDelete")
        if auto_delete_cog:
            loop: disnake.ext.tasks.Loop = auto_delete_cog.deleter
            self.loop_offset = loop.next_iteration
        else:
            self.loop_offset = datetime.now()

    @tasks.loop(hours=168)
    async def cleanup_timers(self):
        await self.bot.wait_until_ready()

        print(f"Cleaning up old /looking-for timers...")

        def expired_timer(pair) -> bool:
            key, value = pair
            if value[0] <= now:
                return False
            return True

        new_lfg_timers = {}
        now = datetime.now().timestamp()

        for user_id, timers in self.lfg_timers.items():
            timers = dict(filter(expired_timer, timers.items()))
            if timers:
                new_lfg_timers[user_id] = timers

        self.lfg_timers = new_lfg_timers
        self.bot.db.jset("lookingforgroup", self.lfg_timers)

    def base_embed(self, title: str, inter: disnake.ApplicationCommandInteraction):
        # Get the offset for this post
        self.get_loop_offset()

        embed = disnake.Embed(timestamp=self.loop_offset + timedelta(days=7))
        embed.title = title
        embed.description = f"{inter.author.mention}\n\nAfter submitting, you won’t be able to " \
                            f"submit another {title} post until <t:{int(embed.timestamp.timestamp())}> " \
                            f"(<t:{int(embed.timestamp.timestamp())}:R>), even if you delete your submission. " \
                            f"A thread will be created for your post which can be used for any corrections or updates."
        embed.set_footer(text=f"User ID: {inter.author.id} - Expires on")

        return embed

    async def post_cooldown(self, inter: disnake.ApplicationCommandInteraction, timer_type: str):
        """Check the cooldown on a posting type for a specific user."""

        timers: dict = self.lfg_timers.get(str(inter.author.id), {})
        timer, message_id = timers.get(timer_type, (0, 0))

        if not timer:
            return False
        elif timer <= datetime.now().timestamp():
            timers.pop(timer_type)
            self.lfg_timers[inter.author.id] = timers
            self.bot.db.jset("lookingforgroup", self.lfg_timers)
            return False

        channel = await inter.guild.fetch_channel(CHANNELS.get(timer_type))

        try:
            message = await channel.fetch_message(message_id)
            message_link = f"\n\nYou can see your previous posting [Here]({message.jump_url})."
        except disnake.errors.NotFound:
            message_link = ""

        await inter.send(
            f"You have to wait until <t:{timer}> (<t:{timer}:R>) to post again.{message_link}",
            ephemeral=True,
            suppress_embeds=True,
        )

        return True

    @commands.user_command(name="Reset - DM", default_member_permissions=disnake.Permissions(moderate_members=True))
    async def user_reset_dm(self, inter: disnake.UserCommandInteraction):
        await self._reset_timer(inter, inter.target, "Dungeon Master")

    @commands.user_command(name="Reset - Players", default_member_permissions=disnake.Permissions(moderate_members=True))
    async def user_reset_players(self, inter: disnake.UserCommandInteraction):
        await self._reset_timer(inter, inter.target, "Players")

    @commands.user_command(name="Reset - Paid", default_member_permissions=disnake.Permissions(moderate_members=True))
    async def user_reset_paid(self, inter: disnake.UserCommandInteraction):
        await self._reset_timer(inter, inter.target, "Paid")

    @commands.user_command(name="Reset - Community", default_member_permissions=disnake.Permissions(moderate_members=True))
    async def user_reset_community(self, inter: disnake.UserCommandInteraction):
        await self._reset_timer(inter, inter.target, "Community")

    async def _reset_timer(
        self,
        inter: disnake.ApplicationCommandInteraction,
        target: disnake.Member,
        lf_type,
    ):
        reset = None

        if str(target.id) in self.lfg_timers:
            reset = self.lfg_timers[str(target.id)].pop(lf_type, None)
            self.bot.db.jset("lookingforgroup", self.lfg_timers)

        if not reset:
            await inter.send(f"{target.mention} had no running timer for {lf_type}", ephemeral=True)
            return

        await inter.send(f"{lf_type} timer reset for {target.mention}", ephemeral=True)

        log_channel = self.bot.get_channel(constants.OUTPUT_CHANNEL_ID)
        await log_channel.send(f"{inter.author.mention} reset {target.mention}'s {lf_type} timer.")

    @commands.slash_command(name="looking-for")
    async def base_slash(self, inter: disnake.ApplicationCommandInteraction):
        ...

    @base_slash.sub_command("dm", description="Players Looking for a Dungeon Master")
    async def dm(self, inter: disnake.ApplicationCommandInteraction):
        lf_type = "Dungeon Master"

        cooldown = await self.post_cooldown(inter, lf_type)
        if cooldown:
            return

        embed = self.base_embed("Player Looking for Dungeon Master", inter)

        for field, values in looking_for_dm.items():
            if field == "opt_in":
                desc = f"{values.desc}\n ❌ Community Games\n❌ Paid Games\n❌ Other Services"
            else:
                desc = f"> *Not Set* - {values.desc}"

            embed.add_field(values.value, desc, inline=False)

        view = DMSubmissionView(bot=self.bot, lf_type=lf_type, lfg_timers=self.lfg_timers)

        await inter.send(embed=embed, ephemeral=True, view=view)

    @base_slash.sub_command("players", description="Dungeon Master Looking for Players")
    async def players(self, inter: disnake.ApplicationCommandInteraction):
        lf_type = "Players"

        cooldown = await self.post_cooldown(inter, lf_type)
        if cooldown:
            return

        embed = self.base_embed("Dungeon Master Looking for Players", inter)

        for field, values in looking_for_players.items():
            embed.add_field(values.value, f"> *Not Set* - {values.desc}", inline=False)

        view = PlayersSubmissionView(bot=self.bot, lf_type=lf_type, lfg_timers=self.lfg_timers)

        await inter.send(embed=embed, ephemeral=True, view=view)

    @base_slash.sub_command("paid", description="Paid Dungeon Master Looking for Players")
    async def paid(self, inter: disnake.ApplicationCommandInteraction):
        lf_type = "Paid"

        cooldown = await self.post_cooldown(inter, lf_type)
        if cooldown:
            return

        embed = self.base_embed("Paid Dungeon Master Looking for Players", inter)

        for field, values in looking_for_paid.items():
            embed.add_field(values.value, f"> *Not Set* - {values.desc}", inline=False)

        view = PaidSubmissionView(bot=self.bot, lf_type=lf_type, lfg_timers=self.lfg_timers)

        await inter.send(embed=embed, ephemeral=True, view=view)

    @base_slash.sub_command("community", description="Community Looking for Members")
    async def community(self, inter: disnake.ApplicationCommandInteraction):
        lf_type = "Community"

        cooldown = await self.post_cooldown(inter, lf_type)
        if cooldown:
            return

        embed = self.base_embed("Looking for Community", inter)

        for field, values in looking_for_community.items():
            embed.add_field(values.value, f"> *Not Set* - {values.desc}", inline=False)

        view = CommunitySubmissionView(bot=self.bot, lf_type=lf_type, lfg_timers=self.lfg_timers)

        await inter.send(embed=embed, ephemeral=True, view=view)


def setup(bot):
    bot.add_cog(LookingForGroup(bot))
