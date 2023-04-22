import discord, os, sys, json, random, logging, time, datetime, contextlib
#from keep_alive import keep_alive
from discord.ext import commands
#from replit import db
from discord import Embed, Color, ui, app_commands
#import sqlite3
from typing import Literal, Optional
from discord.ext.commands import Greedy, Context
from discord.member import VoiceState
import psycopg2 as pgsql

conn = pgsql.connect("dbname=alphawolfie user=postgres password=password")
curr = conn.cursor()
#con = sqlite3.connect('/root/data/data1.db')
#con = sqlite3.connect('data1.db')
#cur = con.cursor()
MY_GUILD = discord.Object(id=468176956232302603)
#print(db['newreacts'])
#emojireacts = db['newreacts']

#0 = on my machine, 1 = on digital ocean
location = 0

if location == 0:
  myprefix = '>'
else:
  myprefix = ';'

#define stuff
def randomtopic():
  l = []
  with open('randomtopics.txt') as f:
    for line in f: 
      l.append(line)
  return random.choice(l)


def is_it_me(ctx):
    return ctx.message.author.id == 585991293377839114

class PersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Agree and Verify!', style=discord.ButtonStyle.green, custom_id='verifybutton')
    async def verify(self,  interaction: discord.Interaction, button: discord.ui.Button):
        print("seen")
        await interaction.response.send_message(content='You have sucessfully verified. Say hi in <#670362292659159040>!', ephemeral=True)
        nusr = interaction.user
        role1 = interaction.guild.get_role(702710000048668783)
        await nusr.add_roles(role1)
        print("added role")
        channel = interaction.guild.get_channel(670362292659159040)
        await channel.send(f'Welcome, <@{nusr.id}> as the {interaction.guild.member_count}th user!')
        await channel.send(f'~{randomtopic()}')  
        

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
    cha = self.client.get_channel(777042897630789633)
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
  @commands.Cog.listener()
  async def on_command_error(self, ctx, error):
    # Send me a dm if needed
    if isinstance(error, commands.CommandNotFound):
      return
    elif isinstance(error, commands.MissingRequiredArgument):
      ctx.command.reset_cooldown(ctx)
      await ctx.send(f'You are missing a required argument. Please use `{ctx.prefix}{ctx.command} {ctx.command.signature}`', delete_after=10)
      return
    elif isinstance(error, commands.MissingPermissions):
      ctx.command.reset_cooldown(ctx)
      await ctx.send(f'You are missing the required permissions to use this command.', delete_after=5)
      return
    elif isinstance(error, commands.CommandOnCooldown):
      await ctx.message.add_reaction('⏱️')
      return
    elif isinstance(error, commands.CheckFailure):
      ctx.command.reset_cooldown(ctx)
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
        if not message.channel.id in [876586125987295283, 876586168953737246]:
          if location == 1: 
            await message.add_reaction(emote) #disable
          i = 0
      elif trigs in (str.lower(msg)):
        emote = emojireacts[trigs]
        if not message.channel.id in [876586125987295283, 876586168953737246]:
          if location == 1: 
            await message.add_reaction(emote) #disable
          i = 0

    if msg.startswith(';'):
      print(str(msg))

  async def on_raw_reaction_add(self, reaction):
    if reaction.channel_id == 901726179818614824:
      guild = self.get_guild(reaction.guild_id)
      channel = self.get_channel(670362292659159040)
      print('Verified user')
      if location == 1:
        await channel.send(f'Welcome, <@{reaction.user_id}> as the {guild.member_count}th user!')
        await channel.send(f'~{randomtopic()}') #disable
  
  async def on_member_join(self, member):
    if member.guild.id == 468176956232302603:
      #print(len(member.roles))
      #memberid = member.id
      #time.sleep(5)
      #guild1 = self.get_guild(468176956232302603)
      #member = await guild1.fetch_member(memberid)
      #print(len(member.roles))
      if len(member.roles) == 1:
        cha1 = self.get_channel(901726179818614824)
        if location == 1: await cha1.send(content=f'*Welcome, <@{member.id}>!* \n `Read above and press Verify!`', delete_after=15) #disable

client = MyClient(command_prefix=myprefix,intents = discord.Intents.all(), case_insensitive=True) #switch prefix!

class HelpEmbed(discord.Embed): # Our embed with some preset attributes to avoid setting it multiple times
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timestamp = datetime.datetime.utcnow()
        text = "Use help [command] or help [category] for more information | <> is required | [] is optional"
        self.set_footer(text=text)
        self.color = Color.dark_green()

class MyHelp(commands.HelpCommand):
    def __init__(self):
      super().__init__( # create our class with some aliases and cooldown
            command_attrs={
                "help": "The help command for the bot",
                "aliases": ['commands',"helps", "helpme", "h"],
                "case_insensitive" : True
            }
        )
    def get_command_signature(self, command):
        return '%s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)

    async def send(self, **kwargs):
        """a short cut to sending to get_destination"""
        await self.get_destination().send(**kwargs)

    async def send_bot_help(self, mapping):
        """triggers when a `<prefix>help` is called"""
        ctx = self.context
        embed = HelpEmbed(title=f"{ctx.me.display_name} Help")
        embed.set_thumbnail(url=ctx.me.display_avatar)
        usable = 0 
        for cog, commands in mapping.items(): #iterating through our mapping of cog: commands
            if filtered_commands := await self.filter_commands(commands): 
                # if no commands are usable in this category, we don't want to display it
                amount_commands = len(filtered_commands)
                usable += amount_commands
                if cog: # getting attributes dependent on if a cog exists or not
                    name = cog.qualified_name
                    description = cog.description or "There's no info on these commands. Yet."
                else:
                    name = "Developer"
                    description = "Developer commands. You cannot view these."
                embed.add_field(name=f"{name} Category [{amount_commands} usable commands]", value=description)
        embed.description = f"{len(client.commands)} commands | {usable} usable" 
        await self.send(embed=embed)

    async def send_command_help(self, command):
        """triggers when a `<prefix>help <command>` is called"""
        signature = self.get_command_signature(command) # get_command_signature gets the signature of a command in <required> [optional]
        embed = HelpEmbed(title=signature, description=command.help or "No help found...")
        if cog := command.cog:
            embed.add_field(name="Category", value=cog.qualified_name)
        can_run = "No"
        # command.can_run to test if the cog is usable
        with contextlib.suppress(commands.CommandError):
            if await command.can_run(self.context):
                can_run = "Yes"           
        embed.add_field(name="Usable", value=can_run)
        if command._buckets and (cooldown := command._buckets._cooldown): # use of internals to get the cooldown of the command
            embed.add_field(
                name="Cooldown",
                value=f"{cooldown.rate} per {cooldown.per:.0f} seconds",)
        await self.send(embed=embed)
        if filtered_commands := await self.filter_commands(commands):
            for command in filtered_commands:
                embed.add_field(name=self.get_command_signature(command), value=command.help or "No help found...")
        await self.send(embed=embed)

    async def send_help_embed(self, title, description, commands): # a helper function to add commands to an embed
        embed = HelpEmbed(title=title, description=description or "No help found...")
        if filtered_commands := await self.filter_commands(commands):
            for command in filtered_commands:
                embed.add_field(name=self.get_command_signature(command), value=command.help or "No help found...")
        await self.send(embed=embed)

    async def send_cog_help(self, cog):
        title = cog.qualified_name or "Developer"
        await self.send_help_embed(f'{title} Category', cog.description, cog.get_commands())

    async def send_group_help(self, group):
        """triggers when a `<prefix>help <group>` is called"""
        title = self.get_command_signature(group)
        await self.send_help_embed(title, group.help, group.commands)
    
    async def command_not_find(self):
        await self.send_help_embed(f'That command or category was not found.')

    


client.help_command = MyHelp()


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



#@commands.command(help='pingpong', aliases=['pong'])
#async def ping(self, ctx):
  #await ctx.send()


try:
  
  if location == 0: 
    f = open("key.txt", 'r')
    key = f.read()
    client.run(key) #switch prefix!!
  else: client.run(os.getenv("DISCORD_TOKEN"))
except Exception:
  exep = sys.exc_info()
  expv = exep[1]
  print('Failed to start:\n%s'%(str(expv)))