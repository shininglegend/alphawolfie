from main import *
from init import conn, curr, MY_GUILD, is_it_me

#commands
@client.command(help='Load an Extension. Dev only')
@commands.has_role(827016494998093834)
async def load(ctx, extension):
  await client.load_extension(f'Cogs.{extension}')
  await ctx.reply('Done!')


@load.error
async def load_error(ctx, error):
  await ctx.reply(f'Error: {error}', delete_after=15)
  await ctx.message.delete()


@client.command(help='Unload an Extension. Dev only')
@commands.has_role(827016494998093834)
async def unload(ctx, extension):
  await client.unload_extension(f'Cogs.{extension}')
  await ctx.reply('Done!')


@unload.error
async def unload_error(ctx, error):
  await ctx.reply(f'Error: {error}', delete_after=15)
  await ctx.message.delete()


#reloads extension
@client.command(help = 'Reload an Extension. Dev only')
@commands.has_guild_permissions(administrator=True)
async def reload(ctx, extension):
  await client.unload_extension(f'Cogs.{extension}')
  time.sleep(2)
  await client.load_extension(f'Cogs.{extension}')
  await ctx.reply('Done!')


'''@reload.error
async def reload_error(ctx, error):
  await ctx.reply(f'Error: {error}', delete_after=15)
  await ctx.message.delete()'''


@client.command(help="List all guilds")
@commands.check(is_it_me)
async def listGuilds(ctx):
  await ctx.author.send("**List of Servers**")
  guilds = client.guilds
  for guild in guilds:
    await ctx.author.send(f"{guild.name}: `{guild.id}`")
  await ctx.send("Done.")


@client.command(help="Remove a guild")
@commands.check(is_it_me)
async def remove(ctx, id):
  guild1 = client.get_guild(int(id))
  await guild1.leave()
  await ctx.send("Done.")


@client.command(help="Send the Verify message")
@commands.check(is_it_me)
async def welcmsg(ctx):
      embed3= Embed(color=Color.green(), title = "Welcome to the Ninja.io official Discord.", description = "Press below to agree to the rules and start chatting!\n`Your failure to read the rules will not stop you from getting punished.` \nIf you need help, just shoot one of the online staff members a message and we will do our best to help.\n\n------\n\n*This server requires Email verification. If you need help, follow this guide: https://support.discordapp.com/hc/en-us/articles/213219267-Resending-Verification-Email*")
      await ctx.message.delete()
      await ctx.send(embed=embed3, view=PersistentView())


@client.tree.command(
    name='alphaping',
    description='Check the bot\'s latency',
)
async def alphaping(interaction: discord.Interaction):
    """Pong!"""
    await interaction.response.send_message(f'Pong! In {round(client.latency * 1000)}ms', ephemeral=True)


@client.command()
@commands.guild_only()
@commands.has_guild_permissions(administrator=True)
async def sync(
  ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
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