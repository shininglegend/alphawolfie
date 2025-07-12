import discord
from discord.ext import commands
from .helpcmd import ModernHelp, HelpEmbed, HelpView


class HybridHelpCommand(commands.HybridCommand):
    """Hybrid help command that works with both slash and prefix commands"""

    def __init__(self, bot):
        self.bot = bot
        self.help_command = ModernHelp(bot)

        super().__init__(
            self.help_callback,
            name="help",
            description="Shows help information for commands and categories",
            aliases=["commands", "helps", "helpme", "h"],
            with_app_command=True
        )

    @discord.app_commands.describe(
        command="The command or category to get help for",
        category="The category to get help for"
    )
    async def help_callback(
        self,
        ctx: commands.Context,
        command: str = None,
        category: str = None
    ):
        """
        Get help information for commands and categories

        Parameters
        ----------
        command : str, optional
            The specific command to get help for
        category : str, optional
            The specific category to get help for
        """
        # Set up the help command context
        self.help_command.context = ctx

        # Determine what type of help to show
        target = command or category

        if not target:
            # Show main help
            mapping = self.help_command.get_bot_mapping()
            await self.help_command.send_bot_help(mapping)
            return

        # Try to find the target (case-insensitive)
        target_lower = target.lower()

        # First, try to find a command
        bot_command = self.bot.get_command(target)
        if not bot_command:
            # Try case-insensitive command search
            for cmd in self.bot.walk_commands():
                if cmd.name.lower() == target_lower or target_lower in [alias.lower() for alias in cmd.aliases]:
                    bot_command = cmd
                    break

        if bot_command:
            await self.help_command.send_command_help(bot_command)
            return

        # Try to find a cog (category)
        cog = None
        for cog_name, cog_obj in self.bot.cogs.items():
            if cog_name.lower() == target_lower:
                cog = cog_obj
                break

        if cog:
            await self.help_command.send_cog_help(cog)
            return

        # Nothing found
        await self.help_command.command_not_found(target)


async def setup_hybrid_help(bot):
    """Set up hybrid help command for the bot"""
    # Remove the default help command
    bot.remove_command('help')

    # Add our hybrid help command
    hybrid_help = HybridHelpCommand(bot)
    bot.add_command(hybrid_help)

    # Also set the help command for the bot
    bot.help_command = ModernHelp(bot)

    return hybrid_help


class SlashHelpCog(commands.Cog):
    """Cog containing slash command implementations for help"""

    def __init__(self, bot):
        self.bot = bot
        self.help_command = ModernHelp(bot)

    @discord.app_commands.command(name="help", description="Get help for commands and categories")
    @discord.app_commands.describe(
        query="Command or category name to get help for"
    )
    async def slash_help(self, interaction: discord.Interaction, query: str = None):
        """Slash command version of help"""
        # Create a fake context for the help command
        ctx = await self.bot.get_context(interaction)
        self.help_command.context = ctx

        if not query:
            # Show main help
            mapping = self.help_command.get_bot_mapping()
            embed = await self.help_command.get_bot_help_embed(mapping)
            view = HelpView(self.help_command, mapping, ctx)
            await interaction.response.send_message(embed=embed, view=view)
            view.message = await interaction.original_response()
            return

        # Search for command or category (case-insensitive)
        query_lower = query.lower()

        # Try to find command
        command = self.bot.get_command(query)
        if not command:
            for cmd in self.bot.walk_commands():
                if cmd.name.lower() == query_lower or query_lower in [alias.lower() for alias in cmd.aliases]:
                    command = cmd
                    break

        if command:
            embed = await self._get_command_embed(command)
            await interaction.response.send_message(embed=embed)
            return

        # Try to find cog
        cog = None
        for cog_name, cog_obj in self.bot.cogs.items():
            if cog_name.lower() == query_lower:
                cog = cog_obj
                break

        if cog:
            embed = await self.help_command.get_cog_help_embed(cog)
            await interaction.response.send_message(embed=embed)
            return

        # Not found
        embed = HelpEmbed(title="❓ Not Found")
        embed.description = f"No command or category named `{query}` was found."
        embed.color = discord.Color.red()
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def _get_command_embed(self, command):
        """Get embed for a specific command"""
        signature = self.help_command.get_command_signature(command)
        embed = HelpEmbed(title=f"🔧 {signature}")
        embed.description = command.help or "No help available"

        if cog := command.cog:
            embed.add_field(name="📁 Category", value=cog.qualified_name, inline=True)

        # Check if command can be run
        can_run = "❌ No"
        try:
            if await command.can_run(self.help_command.context):
                can_run = "✅ Yes"
        except:
            pass
        embed.add_field(name="🔓 Usable", value=can_run, inline=True)

        # Add cooldown info
        if command._buckets and (cooldown := command._buckets._cooldown):
            embed.add_field(
                name="⏱️ Cooldown",
                value=f"{cooldown.rate} per {cooldown.per:.0f} seconds",
                inline=True
            )

        # Add aliases
        if command.aliases:
            embed.add_field(
                name="🔗 Aliases",
                value=", ".join(f"`{alias}`" for alias in command.aliases),
                inline=True
            )

        return embed


async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(SlashHelpCog(bot))
