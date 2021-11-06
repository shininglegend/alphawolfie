import discord, os, sys, json, random, logging, time, datetime
from discord.ext import commands
from discord import Embed, Color, ui
import sqlite3

from discord.member import VoiceState

con = sqlite3.connect('data1.db')
cur = con.cursor()

#define stuff
def prcscmd(cmds):
  cmdprefix = cmds[0]
  cmds = cmds[1:]
  cmd = cmds.split(' ')
  cmd = cmd[0]
  return cmd

def prcsargs(cmds):
  cmds = cmds[1:]
  args = cmds.split(' ')
  if len(args) > 1:
    args = args[1:]
  else:
    args = None
  return args

def is_it_me(ctx):
    return ctx.message.author.id == 585991293377839114

class PersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Agree and Verify!', style=discord.ButtonStyle.green, custom_id='verifybutton')
    async def verify(self, button: discord.ui.Button, interaction: discord.Interaction):
        print("seen")
        nusr = interaction.user
        role1 = interaction.guild.get_role(702710000048668783)
        await nusr.add_roles(role1)
        print("added role")
        channel = interaction.guild.get_channel(670362292659159040)
        await channel.send(f'Welcome, <@{nusr.id}> as the {interaction.guild.member_count}th user!')
        await interaction.response.send_message(content='You have sucessfully verified. Say hi in <#670362292659159040>!', ephemeral=True)
        

class MyClient(commands.Bot):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.persistent_views_added = False


  async def logEvent(self, message, title=None):
    cha = self.client.get_channel(777042897630789633)
    if not title:
      title="Logged Event:"
    embed3 = Embed(title=title, description=message, color=Color.green(), timestamp=datetime.datetime)
    await cha.send(embed=embed3)

  async def on_ready(self):
    if not self.persistent_views_added:
      self.add_view(PersistentView())
      self.persistent_views_added = True
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
    cur.execute('SELECT * FROM reactions')
    for row in cur.fetchall():
      emojireacts[row[1]] = row[2]
    
    #print(emojireacts)

    for trigs in emojireacts:
      if trigs in (str.lower(msg)):
        #emote = self.get_emoji(int(emojireacts[trigs]))
        emote = emojireacts[trigs]
        #emote = class(emote)
        #print(emojireacts[trigs])
        if not message.channel.id in [876586125987295283, 876586168953737246]:
          await message.add_reaction(emote)
          i = 0

    if msg.startswith(';'):
      msg1 = str(msg)
      print(msg1)
      if len(message.mentions) > 0:
        usrsId = message.mentions

      cmd = prcscmd(msg1)
      args = prcsargs(msg1)

  async def on_raw_reaction_add(self, reaction):
    if reaction.channel_id == 783900263274512404 and reaction.message_id == 783905519789801472:
      guild = self.get_guild(reaction.guild_id)
      channel = self.get_channel(670362292659159040)
      print('Verified user')
      await channel.send(f'Welcome, <@{reaction.user_id}> as the {guild.member_count}th user!')
  
  async def on_member_join(self, member):
    if member.guild.id == 468176956232302603 and len(member.roles) == 1:
      cha1 = self.get_channel(901726179818614824)
      await cha1.send(content=f'*Welcome, <@{member.id}>!* \n `Read above and press Verify!`', delete_after=15)


client = MyClient(command_prefix='>',intents = discord.Intents.all())


#commands
@client.command(help='Load an Extension. Dev only')
@commands.has_role(827016494998093834)
async def load(ctx, extension):
  client.load_extension(f'Cogs.{extension}')
  await ctx.reply('Done!')

@load.error
async def load_error(ctx, error):
  await ctx.reply(f'Error: {error}', delete_after=15)
  await ctx.message.delete()

@client.command(help='Unload an Extension. Dev only')
@commands.has_role(827016494998093834)
async def unload(ctx, extension):
  client.unload_extension(f'Cogs.{extension}')
  await ctx.reply('Done!')

@unload.error
async def unload_error(ctx, error):
  await ctx.reply(f'Error: {error}', delete_after=15)
  await ctx.message.delete()

#reloads extension
@client.command(help = 'Reload an Extension. Dev only')
@commands.has_guild_permissions(administrator=True)
async def reload(ctx, extension):
  client.unload_extension(f'Cogs.{extension}')
  time.sleep(2)
  client.load_extension(f'Cogs.{extension}')
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

for filename in os.listdir('Cogs'):
    if filename.endswith('.py'):
        client.load_extension('Cogs.'+filename[:-3])

try:
  client.run(os.getenv("DISCORD_TOKEN"))
except Exception:
  exep = sys.exc_info()
  expv = exep[1]
  print('Failed to start:\n%s'%(str(expv))) 
#if this is visable it was successful... I think?
