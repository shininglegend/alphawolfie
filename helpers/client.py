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
    embed3 = Embed(title=title, description=message, color=Color.green(), timestamp=datetime.datetime)
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

  async def on_message(self, message):
    await self.process_commands(message)
    if message.author == self.user:
      return
    #print(message.content)
    msg = message.content
    
    #emojireacts = db['newreacts']
    emojireacts = {}
    curr.execute('SELECT * FROM reactions')
    for row in curr.fetchall():
      emojireacts[row[1]] = row[2]
    
    #print(emojireacts)
    #print(message.mentions)
    mentions = []
    for mention in message.mentions:
      mentions.append(str(mention.id))
    #print(mentions)
    for trigs in emojireacts:
      if trigs in mentions:
        print('found mention: '+trigs)
        emote = emojireacts[trigs]
        print(emote)
        if not message.channel.id in [876586125987295283, 876586168953737246]:
          if location == 1: 
            await message.add_reaction(emote) #disable
          i = 0
      elif trigs in (str.lower(msg)):
        emote = emojireacts[trigs]
        if not message.channel.id in [876586125987295283, 876586168953737246]:
          if location == 1: 
            try:
              await message.add_reaction(emote) #disable
            except discord.errors.HTTPException:
              print('Unknown Emoji: '+emote)
              await self.logEvent('Unknown Emoji: '+emote)
          i = 0

    if msg.startswith(';'):
      print(str(msg))

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