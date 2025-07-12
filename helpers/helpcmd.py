import datetime
import contextlib
from typing import Optional, List
from discord.ext import commands
from discord import Color, Embed, ButtonStyle, SelectOption
from discord.ui import Button, Select, View


class HelpEmbed(Embed):
    """Enhanced embed with preset attributes and modern datetime usage"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timestamp = datetime.datetime.now(datetime.timezone.utc)
        self.color = Color.dark_green()
        self.set_footer(text="<> required | [] optional")


class HelpView(View):
    """Interactive view for help command navigation"""

    def __init__(self, help_command, mapping, ctx):
        super().__init__(timeout=180)
        self.help_command = help_command
        self.mapping = mapping
        self.ctx = ctx
        self.current_page = "main"

        # Add category select menu
        self.add_item(CategorySelect(help_command, mapping, ctx))

        # Add navigation buttons
        self.add_item(HomeButton())
        self.add_item(CommandsButton())

    async def on_timeout(self):
        """Disable all components when view times out"""
        for item in self.children:
            item.disabled = True
        try:
            await self.message.edit(view=self)
        except:
            pass


class CategorySelect(Select):
    """Select menu for choosing help categories"""

    def __init__(self, help_command, mapping, ctx):
        self.help_command = help_command
        self.mapping = mapping
        self.ctx = ctx

        options = [
            SelectOption(label="🏠 Home", value="home", description="Main help page")
        ]

        for cog, commands in mapping.items():
            if cog and cog.qualified_name:
                filtered_commands = []
                try:
                    filtered_commands = [cmd for cmd in commands if not cmd.hidden]
                except:
                    pass

                if filtered_commands:
                    name = cog.qualified_name
                    description = (
                        cog.description[:50] + "..."
                        if len(cog.description or "") > 50
                        else cog.description
                    )
                    options.append(
                        SelectOption(
                            label=f"📁 {name}",
                            value=name.lower(),
                            description=description or "No description available",
                        )
                    )

        super().__init__(placeholder="Choose a category...", options=options[:25])

    async def callback(self, interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(
                "Only the command author can use this menu.", ephemeral=True
            )
            return

        await interaction.response.defer()

        if self.values[0] == "home":
            embed = await self.help_command.get_bot_help_embed(self.mapping)
        else:
            # Find cog by case-insensitive name
            selected_cog = None
            for cog in self.mapping.keys():
                if cog and cog.qualified_name.lower() == self.values[0]:
                    selected_cog = cog
                    break

            if selected_cog:
                embed = await self.help_command.get_cog_help_embed(selected_cog)
            else:
                embed = HelpEmbed(
                    title="Category Not Found",
                    description="The selected category could not be found.",
                )

        await interaction.edit_original_response(embed=embed)


class HomeButton(Button):
    """Button to return to main help page"""

    def __init__(self):
        super().__init__(style=ButtonStyle.primary, label="🏠 Home", row=1)

    async def callback(self, interaction):
        view = self.view
        if interaction.user != view.ctx.author:
            await interaction.response.send_message(
                "Only the command author can use this button.", ephemeral=True
            )
            return

        await interaction.response.defer()
        embed = await view.help_command.get_bot_help_embed(view.mapping)
        await interaction.edit_original_response(embed=embed)


class CommandsButton(Button):
    """Button to show all commands"""

    def __init__(self):
        super().__init__(style=ButtonStyle.secondary, label="📋 All Commands", row=1)

    async def callback(self, interaction):
        view = self.view
        if interaction.user != view.ctx.author:
            await interaction.response.send_message(
                "Only the command author can use this button.", ephemeral=True
            )
            return

        await interaction.response.defer()
        embed = await view.help_command.get_all_commands_embed(view.mapping)
        await interaction.edit_original_response(embed=embed)


class ModernHelp(commands.HelpCommand):
    """Modern help command with interactive UI and case-insensitive matching"""

    def __init__(self, client):
        super().__init__(
            command_attrs={
                "help": "Shows help information for commands and categories",
                "aliases": ["commands", "helps", "helpme", "h"],
                "case_insensitive": True,
                "cooldown": commands.CooldownMapping.from_cooldown(
                    1, 5, commands.BucketType.user
                ),
            }
        )
        self.client = client

    def get_command_signature(self, command):
        """Get formatted command signature"""
        return (
            f"{self.context.clean_prefix}{command.qualified_name} {command.signature}"
        )

    async def send(self, **kwargs):
        """Send message to destination"""
        await self.get_destination().send(**kwargs)

    async def filter_commands(self, bot_commands, *, sort=False, key=None):
        """Filter and sort commands based on permissions"""
        if sort and key is None:
            key = lambda c: c.name

        iterator = bot_commands if not sort else sorted(bot_commands, key=key)

        async def predicate(cmd):
            try:
                return await cmd.can_run(self.context)
            except commands.CommandError:
                return False

        ret = []
        for cmd in iterator:
            if not cmd.hidden and await predicate(cmd):
                ret.append(cmd)

        return ret

    async def get_bot_help_embed(self, mapping):
        """Generate main help embed"""
        ctx = self.context
        embed = HelpEmbed(title=f"{ctx.me.display_name} Help")
        embed.set_thumbnail(url=ctx.me.display_avatar.url)

        total_commands = 0
        category_info = []

        for cog, bot_commands in mapping.items():
            if filtered_commands := await self.filter_commands(bot_commands, sort=True):
                if not filtered_commands:
                    continue

                total_commands += len(filtered_commands)

                if cog:
                    name = cog.qualified_name
                    description = cog.description or "No description available"
                    category_info.append(
                        f"**{name}** - {len(filtered_commands)} commands\n{description[:100]}{'...' if len(description) > 100 else ''}"
                    )

        embed.description = f"**{total_commands}** commands available."

        if category_info:
            embed.add_field(
                name="📁 Categories",
                value="\n\n".join(category_info[:10]),
                # Limit to prevent embed size issues
                inline=True,
            )

        return embed

    async def get_cog_help_embed(self, cog):
        """Generate category help embed"""
        embed = HelpEmbed(title=f"📁 {cog.qualified_name} Category")
        embed.description = cog.description or "No description available"

        if filtered_commands := await self.filter_commands(
            cog.get_commands(), sort=True
        ):
            command_list = []
            for command in filtered_commands:
                help_text = command.help or "No help available"
                command_list.append(
                    f"**{self.get_command_signature(command)}**\n{help_text[:100]}{'...' if len(help_text) > 100 else ''}"
                )

            # Split into multiple fields if too many commands
            chunk_size = 5
            for i in range(0, len(command_list), chunk_size):
                chunk = command_list[i : i + chunk_size]
                field_name = "Commands" if i == 0 else "Commands (continued)"
                embed.add_field(name=field_name, value="\n\n".join(chunk), inline=False)
        else:
            embed.add_field(
                name="No Commands",
                value="No usable commands in this category.",
                inline=False,
            )

        return embed

    async def get_all_commands_embed(self, mapping):
        """Generate embed with all commands"""
        embed = HelpEmbed(title="📋 All Commands")

        all_commands = []
        for cog, bot_commands in mapping.items():
            if filtered_commands := await self.filter_commands(bot_commands, sort=True):
                for command in filtered_commands:
                    category = cog.qualified_name if cog else "Other"
                    all_commands.append(f"**{command.name}** ({category})")

        if all_commands:
            # Group commands by chunks to fit in embed
            chunk_size = 20
            for i in range(0, len(all_commands), chunk_size):
                chunk = all_commands[i : i + chunk_size]
                field_name = "Commands" if i == 0 else f"Commands ({i//chunk_size + 1})"
                embed.add_field(name=field_name, value="\n".join(chunk), inline=True)
        else:
            embed.add_field(
                name="No Commands", value="No usable commands found.", inline=False
            )

        return embed

    async def send_bot_help(self, mapping):
        """Send main help page with interactive UI"""
        embed = await self.get_bot_help_embed(mapping)
        view = HelpView(self, mapping, self.context)
        message = await self.send(embed=embed, view=view)
        view.message = message

    async def send_command_help(self, command):
        """Send help for specific command"""
        signature = self.get_command_signature(command)
        embed = HelpEmbed(title=f"🔧 {signature}")
        embed.description = command.help or "No help available"

        # Add command details
        if cog := command.cog:
            embed.add_field(name="📁 Category", value=cog.qualified_name, inline=True)

        # Check if command can be run
        can_run = "❌ No"
        with contextlib.suppress(commands.CommandError):
            if await command.can_run(self.context):
                can_run = "✅ Yes"
        embed.add_field(name="🔓 Usable", value=can_run, inline=True)

        # Add cooldown information
        if command._buckets and (cooldown := command._buckets._cooldown):
            embed.add_field(
                name="⏱️ Cooldown",
                value=f"{cooldown.rate} per {cooldown.per:.0f} seconds",
                inline=True,
            )

        # Add aliases if any
        if command.aliases:
            embed.add_field(
                name="🔗 Aliases",
                value=", ".join(f"`{alias}`" for alias in command.aliases),
                inline=True,
            )

        # Add subcommands for groups
        if isinstance(command, commands.Group):
            if filtered_commands := await self.filter_commands(
                command.commands, sort=True
            ):
                subcommand_list = []
                for subcommand in filtered_commands:
                    help_text = subcommand.help or "No help available"
                    subcommand_list.append(
                        f"**{self.get_command_signature(subcommand)}**\n{help_text[:80]}{'...' if len(help_text) > 80 else ''}"
                    )

                embed.add_field(
                    name="📋 Subcommands",
                    value="\n\n".join(
                        subcommand_list[:5]
                    ),  # Limit to prevent embed size issues
                    inline=False,
                )

        await self.send(embed=embed)

    async def send_cog_help(self, cog):
        """Send help for specific category"""
        embed = await self.get_cog_help_embed(cog)
        await self.send(embed=embed)

    async def send_group_help(self, group):
        """Send help for command group"""
        await self.send_command_help(group)

    async def command_not_found(self, string):
        """Handle command not found with suggestions"""
        embed = HelpEmbed(title="❓ Command Not Found")
        embed.description = f"No command or category named `{string}` was found."

        # Try to find similar commands
        all_commands = []
        for cog, bot_commands in self.get_bot_mapping().items():
            if filtered_commands := await self.filter_commands(bot_commands):
                all_commands.extend(cmd.name for cmd in filtered_commands)
            if cog:
                all_commands.append(cog.qualified_name.lower())

        # Simple similarity check
        suggestions = []
        string_lower = string.lower()
        for cmd in all_commands:
            if string_lower in cmd.lower() or cmd.lower() in string_lower:
                suggestions.append(cmd)

        if suggestions:
            embed.add_field(
                name="💡 Did you mean?",
                value="\n".join(f"• `{suggestion}`" for suggestion in suggestions[:5]),
                inline=False,
            )

        embed.add_field(
            name="💬 Usage",
            value=f"Use `{self.context.clean_prefix}help` to see all available commands.",
            inline=False,
        )

        await self.send(embed=embed)

    async def subcommand_not_found(self, command, string):
        """Handle subcommand not found"""
        embed = HelpEmbed(title="❓ Subcommand Not Found")
        embed.description = (
            f"Command `{command.qualified_name}` has no subcommand named `{string}`."
        )

        if isinstance(command, commands.Group) and command.commands:
            available = [cmd.name for cmd in command.commands if not cmd.hidden]
            if available:
                embed.add_field(
                    name="📋 Available subcommands",
                    value="\n".join(f"• `{name}`" for name in available[:10]),
                    inline=False,
                )

        await self.send(embed=embed)

    async def send_error_message(self, error):
        """Send error message with helpful information"""
        embed = HelpEmbed(title="❌ Error")
        embed.description = str(error)
        embed.color = Color.red()
        await self.send(embed=embed)
