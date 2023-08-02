import discord, time
from discord.ext import commands
from discord.ext.commands import Greedy, Context
#from replit import db
from typing import Literal, Optional
#import sqlite3

from init import is_it_me, location



#commands

class DevOnly(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.description = "Developer commands. You cannot view these."

  @commands.Cog.listener()
  async def on_ready(self):
    print('DevOnly is online')

  @commands.command(help='Load an Extension. Dev only')
  @commands.has_role(827016494998093834)
  async def load(self, ctx, extension):
    await self.bot.load_extension(f'Cogs.{extension}')
    await ctx.reply('Done!')


  @load.error
  async def load_error(self, ctx, error):
    await ctx.reply(f'Error: {error}', delete_after=15)
    await ctx.message.delete()


  @commands.command(help='Unload an Extension. Dev only')
  @commands.has_role(827016494998093834)
  async def unload(self, ctx, extension):
    await self.bot.unload_extension(f'Cogs.{extension}')
    await ctx.reply('Done!')


  @unload.error
  async def unload_error(self, ctx, error):
    await ctx.reply(f'Error: {error}', delete_after=15)
    await ctx.message.delete()


  #reloads extension
  @commands.command(help = 'Reload an Extension. Dev only')
  @commands.has_guild_permissions(administrator=True)
  async def reload(self, ctx, extension):
    await self.bot.unload_extension(f'Cogs.{extension}')
    time.sleep(2)
    await self.bot.load_extension(f'Cogs.{extension}')
    await ctx.reply('Done!')


  '''@reload.error
  async def reload_error(ctx, error):
    await ctx.reply(f'Error: {error}', delete_after=15)
    await ctx.message.delete()'''


  @commands.command(help="List all guilds")
  @commands.check(is_it_me)
  async def listGuilds(self, ctx):
    await ctx.author.send("**List of Servers**")
    guilds = self.bot.guilds
    for guild in guilds:
      await ctx.author.send(f"{guild.name}: `{guild.id}`")
    await ctx.send("Done.")


  @commands.command(help="Remove a guild")
  @commands.check(is_it_me)
  async def remove(self, ctx, id):
    guild1 = self.bot.get_guild(int(id))
    await guild1.leave()
    await ctx.send("Done.")


  # @commands.command(help="Send the Verify message")
  # @commands.check(is_it_me)
  # async def welcmsg(self, ctx):
  #       embed3= Embed(color=Color.green(), title = "Welcome to the Ninja.io official Discord.", description = "Press below to agree to the rules and start chatting!\n`Your failure to read the rules will not stop you from getting punished.` \nIf you need help, just shoot one of the online staff members a message and we will do our best to help.\n\n------\n\n*This server requires Email verification. If you need help, follow this guide: https://support.discordapp.com/hc/en-us/articles/213219267-Resending-Verification-Email*")
  #       await ctx.message.delete()
  #       await ctx.send(embed=embed3, view=PersistentView())


  @commands.hybrid_command()
  async def alphaping(self, ctx):
      """Pong!"""
      await ctx.send(f'Pong! In {round(self.bot.latency * 1000)}ms', ephemeral=True)


  @commands.command()
  @commands.guild_only()
  @commands.has_guild_permissions(administrator=True)
  async def sync(self, ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
      if not guilds:
          if spec == "~":
              synced = await ctx.bot.tree.sync(guild=ctx.guild)
          elif spec == "*":
              ctx.bot.tree.copy_global_to(guild=ctx.guild)
              synced = await ctx.bot.tree.sync(guild=ctx.guild)
          elif spec == "^":
              ctx.bot.tree.clear_commands(guild=ctx.guild)
              await ctx.bot.tree.sync(guild=ctx.guild)
              synced = []
          else:
              synced = await ctx.bot.tree.sync()

          await ctx.send(
              f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
          )
          return

      ret = 0
      for guild in guilds:
          try:
              await ctx.bot.tree.sync(guild=guild)
          except discord.HTTPException:
              pass
          else:
              ret += 1

      await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

async def setup(bot):
  await bot.add_cog(DevOnly(bot))