from init import *
import discord, os, datetime
from discord.ext import commands
from discord import Embed, Color

from helpers.verify import PersistentView, randomtopic

class MyClient(commands.Bot):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.persistent_views_added = False
    #self.tree = app_commands.CommandTree(self)
  
  async def setup_hook(self):
    for filename in os.listdir('Cogs'):
      if filename.endswith('.py'):
        await self.load_extension('Cogs.'+filename[:-3])
    self.tree.copy_global_to(guild=MY_GUILD)
    await self.tree.sync(guild=MY_GUILD)
    print("Loaded Cogs and Synced Slash Commands")

  async def logEvent(self, message, title=None):
    cha = self.get_channel(777042897630789633)
    if not title:
      title="Logged Event:"
    embed3 = Embed(title=title, description=message, color=Color.green(), timestamp=datetime.datetime.now())
    await cha.send(embed=embed3)

  async def logerrors(self, message, ctx=None):
    # Send me a dm on error
    # First print the error
    print(message)
    print(ctx)
    # select a channel based on whether we are on the beta or not
    if location == 1: #  digital ocean
      cha = await self.fetch_channel(853005257528049704)
    else: # on my machine
      cha = await self.fetch_channel(906061945591963648)
    embed3 = Embed(title="Error:", description=message, color=Color.red(), timestamp=datetime.datetime.now())
    if ctx:
      embed3.add_field(name="Command:", value=ctx.message.content)
      embed3.add_field(name="Author:", value=f'{ctx.author.name}#{ctx.author.discriminator}')
      embed3.add_field(name="Author ID:", value=ctx.author.id)
      embed3.add_field(name="Channel:", value=ctx.channel.name)
      embed3.add_field(name="Channel Link:", value=f'<#{ctx.channel.id}>')
    await cha.send(embed=embed3)
  
  # Error handling
  if location == 1: # only on digital ocean
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
      # Send me a dm if needed ()
      if isinstance(error, commands.CommandNotFound):
        return
      elif isinstance(error, commands.CommandOnCooldown):
        await ctx.message.add_reaction('⏱️')
        return
      elif isinstance(error, commands.MissingRequiredArgument):
        ctx.command.reset_cooldown(ctx)
        await ctx.send(f'You are missing a required argument. Please use `{ctx.prefix}{ctx.command} {ctx.command.signature}`', delete_after=10)
        return
      elif isinstance(error, commands.MissingPermissions):
        ctx.command.reset_cooldown(ctx)
        await ctx.send(f'You are missing the required permissions to use this command.', delete_after=5)
        return
      elif isinstance(error, commands.CheckFailure):
        ctx.command.reset_cooldown(ctx)
        await ctx.send(f'Wrong channel, or missing permissions.', delete_after=5)
        return
      elif isinstance(error, commands.BadArgument):
        ctx.command.reset_cooldown(ctx)
        await ctx.send(f'You have entered a bad argument. Please use `{ctx.prefix}{ctx.command} {ctx.command.signature}`', delete_after=10)
        return
      elif isinstance(error, commands.CheckFailure):
        await ctx.send(f'You are missing the required permissions to use this command.', delete_after=5)
        return
      else:
        ctx.command.reset_cooldown(ctx)
        await ctx.send(f'An error has occured. If this continues to happen, please open a support ticket.', delete_after=5)
        await self.logerrors(str(error), ctx)
        return

  async def on_ready(self):
    if not self.persistent_views_added:
      self.add_view(PersistentView())
      self.persistent_views_added = True
      print('Added VerifyView')
    print('Logged in as:')
    print(self.user.name)
    print(self.user.id)
    print('------')
    game = discord.Game("https://ninja.io")
    await self.change_presence(status=discord.Status.dnd, activity=game)

  # Helper function to fetch emoji reactions from the database
  def fetch_emoji_reactions(self):
    # Initialize an empty dictionary to hold emoji reactions
    emojireacts = {}
    # Execute a query to select all reactions from the database
    curr.execute('SELECT * FROM reactions')
    for row in curr.fetchall():  # Fetch all rows from the query result
        emojireacts[row[1]] = row[2]  # Map each trigger to its corresponding emoji
    return emojireacts
  
  async def on_message(self, message):
    # Process any commands that might be in the message
    await self.process_commands(message)
    
    # Ignore messages sent by the bot itself to prevent self-responses
    if message.author == self.user:
        return

    # Fetch emoji reactions from the database
    emojireacts = self.fetch_emoji_reactions()
    
    # Extract IDs of all mentioned users in the message for easy lookup
    mentions = [str(mention.id) for mention in message.mentions]

    # Iterate over each trigger in the emoji reactions
    for trigger, emote in emojireacts.items():
        # Check if the trigger is in the mentions or in the message content (case-insensitive)
        if trigger in mentions or trigger in message.content.lower():
            # Check if the message is not in a specific channel and location is set to 1 before reacting
            if message.channel.id not in [876586125987295283, 876586168953737246] and location == 1:
                try:
                    # Attempt to add the reaction to the message
                    await message.add_reaction(emote)
                except discord.errors.HTTPException:
                    # If there's an HTTPException (e.g., emoji not found), use a fallback emoji
                    fallback_emoji = self.get_emoji(1208944867305066516)
                    await message.add_reaction(fallback_emoji)

    # Special handling for messages that start with ';', for example, logging or special commands
    if message.content.startswith(';'):
        print(message.content)

  # async def on_raw_reaction_add(self, reaction):
  #   if reaction.channel_id == 901726179818614824:
  #     guild = self.get_guild(reaction.guild_id)
  #     channel = self.get_channel(670362292659159040)
  #     print('Verified user')
  #     if location == 1:
  #       await channel.send(f'Welcome, <@{reaction.user_id}> as the {guild.member_count}th user!')
  #       await channel.send(f'~{randomtopic()}') #disable
  
  # async def on_member_join(self, member):
  #   if member.guild.id == 468176956232302603:
  #     #print(len(member.roles))
  #     #memberid = member.id
  #     #time.sleep(5)
  #     #guild1 = self.get_guild(468176956232302603)
  #     #member = await guild1.fetch_member(memberid)
  #     #print(len(member.roles))
  #     if len(member.roles) == 1:
  #       cha1 = self.get_channel(901726179818614824)
  #       if location == 1: await cha1.send(content=f'*Welcome, <@{member.id}>!* \n `Read above and press Verify!`', delete_after=15) #disable