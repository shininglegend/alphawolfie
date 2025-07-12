"""
Setup utility for integrating the modernized help system into the bot.
This module provides easy setup functions for both the traditional help command
and the hybrid help command that supports both prefix and slash commands.
"""

import logging
from discord.ext import commands
from .helpcmd import ModernHelp
from .help_hybrid import HybridHelpCommand, SlashHelpCog

logger = logging.getLogger(__name__)


async def setup_modern_help(bot: commands.Bot, use_hybrid: bool = True):
    """
    Set up the modern help system for the bot.

    Args:
        bot: The Discord bot instance
        use_hybrid: Whether to use hybrid commands (supports both prefix and slash)

    Returns:
        The help command instance that was set up
    """
    try:
        # Remove the default help command if it exists
        if bot.help_command:
            bot.remove_command('help')
            logger.info("Removed default help command")

        if use_hybrid:
            # Set up hybrid help system
            logger.info("Setting up hybrid help system...")

            # Add the slash help cog
            await bot.add_cog(SlashHelpCog(bot))
            logger.info("Added SlashHelpCog")

            # Set up the traditional help command
            help_command = ModernHelp(bot)
            bot.help_command = help_command
            logger.info("Set up ModernHelp as bot.help_command")

            return help_command
        else:
            # Set up traditional help only
            logger.info("Setting up traditional help system...")
            help_command = ModernHelp(bot)
            bot.help_command = help_command
            logger.info("Set up ModernHelp as bot.help_command")

            return help_command

    except Exception as e:
        logger.error(f"Failed to setup help system: {e}")
        raise


def setup_traditional_help_only(bot: commands.Bot):
    """
    Set up only the traditional help command (no slash command support).

    Args:
        bot: The Discord bot instance

    Returns:
        The ModernHelp instance
    """
    try:
        # Remove existing help command
        if bot.help_command:
            bot.remove_command('help')
            logger.info("Removed default help command")

        # Set up modern help
        help_command = ModernHelp(bot)
        bot.help_command = help_command
        logger.info("Set up traditional ModernHelp")

        return help_command

    except Exception as e:
        logger.error(f"Failed to setup traditional help: {e}")
        raise


async def setup_slash_help_only(bot: commands.Bot):
    """
    Set up only slash command help (removes traditional help command).

    Args:
        bot: The Discord bot instance

    Returns:
        The SlashHelpCog instance
    """
    try:
        # Remove existing help command completely
        if bot.help_command:
            bot.help_command = None
            logger.info("Disabled traditional help command")

        # Add slash help cog
        cog = SlashHelpCog(bot)
        await bot.add_cog(cog)
        logger.info("Set up slash-only help system")

        return cog

    except Exception as e:
        logger.error(f"Failed to setup slash help: {e}")
        raise


def get_help_stats(bot: commands.Bot):
    """
    Get statistics about the bot's commands for help system debugging.

    Args:
        bot: The Discord bot instance

    Returns:
        Dictionary containing help statistics
    """
    stats = {
        'total_commands': len(list(bot.walk_commands())),
        'cogs': len(bot.cogs),
        'hidden_commands': len([cmd for cmd in bot.walk_commands() if cmd.hidden]),
        'help_command_type': type(bot.help_command).__name__ if bot.help_command else None,
        'has_slash_help': 'SlashHelpCog' in bot.cogs,
        'command_categories': {}
    }

    # Count commands per category
    for cog_name, cog in bot.cogs.items():
        command_count = len(cog.get_commands())
        if command_count > 0:
            stats['command_categories'][cog_name] = command_count

    # Count uncategorized commands
    uncategorized = len([cmd for cmd in bot.walk_commands() if not cmd.cog])
    if uncategorized > 0:
        stats['command_categories']['Uncategorized'] = uncategorized

    return stats


# Backwards compatibility aliases
setup_help = setup_modern_help  # For existing code that might use this name
ModernHelpCommand = ModernHelp  # Alternative name for the help command class
