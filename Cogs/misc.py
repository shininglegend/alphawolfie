import discord, os, sys, json, random, logging, requests, datetime, asyncio
from discord.ext import commands
#from replit import db
from discord import Embed, Color
import psycopg2 as pgsql

from init import conn, curr, location

MEDIA_CHANNEL_IDS = [835164179001901099, 911020430368866314, 1365612478939271261]
# These roles bypass the media check
ROLE_IDS = [470547452873932806, 670427731468746783] 

def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  print(str(json_data))
  quote = json_data[0]['q'] + """ 
  *""" + json_data[0]['a'] + "*"
  return(quote)


def randomtopic():
  l = []
  with open('randomtopics.txt') as f:
    for line in f: 
      l.append(line)
  return random.choice(l)


class Misc(commands.Cog):

    def __init__(self, bot):
      self.bot = bot
      self.description = 'This is where all the extra commands go.'

    async def log0101(self, message, title=None):
      cha = await self.bot.fetch_channel(777042897630789633)
      if not title:
        title="Logged Event:"
      embed3 = Embed(title=title, description=message, color=Color.green(), timestamp=datetime.datetime.now())
      await cha.send(embed=embed3)
    #events

    @commands.Cog.listener()
    async def on_ready(self):
      print('Misc is online')

    @commands.Cog.listener()
    async def on_message(self, message):
      if message.channel.id == 1066091397809188904:
        if message.content not in ['ok', 'ck']:
          await message.delete(delay=1)
      # Delete non-media messages
      if message.channel.id not in MEDIA_CHANNEL_IDS:
          return

      user_roles_ids = {role.id for role in message.author.roles}
      user_has_role = any(role_id in user_roles_ids for role_id in ROLE_IDS)

      if not user_has_role and not message.attachments:
        await message.delete()
        await message.author.send(
            f'Your message in <#{message.channel.id}> was deleted because it did not have an attachment. '
            f'Here\'s the message for reference: {message.content}'
        )
        await self.log0101(message=f'<@{message.author.id}> in <#{message.channel.id}> : {message.content}', title='Deleted message')   
        #print('Deleted message')

      # This adds reactions in the map design channel
      if message.attachments and message.channel.id == 911020430368866314:
        # create a thread
        await message.create_thread(name=f'{message.author.name}\'s map', auto_archive_duration=1440)
        # add reactions based on if we have custom emojis or not
        try:
          await message.add_reaction("<:upvote:904548817783894026>")
          await message.add_reaction("<:downvote:904548736884150292>")
        except discord.errors.HTTPException:
          await message.clear_reactions()
          await message.add_reaction("👍")
          await message.add_reaction("👎")

      # This adds reactions in the weapon design channel
      if message.attachments and message.channel.id == 1365612478939271261:
        # create a thread
        await message.create_thread(name=f'{message.author.name}\'s weapon', auto_archive_duration=1440)
        # add reactions based on if we have custom emojis or not
        try:
          await message.add_reaction("<:upvote:904548817783894026>")
          await message.add_reaction("<:downvote:904548736884150292>")
        except discord.errors.HTTPException:
          await message.clear_reactions()
          await message.add_reaction("👍")
          await message.add_reaction("👎")

    @commands.Cog.listener()
    async def on_message_edit(self, msgbefore, message):
      # Delete non-media messages on edit
      # Delete non-media messages
      if message.channel.id not in MEDIA_CHANNEL_IDS:
          return

      user_roles_ids = {role.id for role in message.author.roles}
      user_has_role = any(role_id in user_roles_ids for role_id in ROLE_IDS)

      if not user_has_role and not message.attachments:
        await message.author.send(
            f'Your message in <#{message.channel.id}> was deleted because it did not have an attachment. '
            f'Here\'s the message for reference: {message.content}'
        )
        await self.log0101(message=f'<@{message.author.id}> in <#{message.channel.id}> : {message.content}', title='Deleted message')
        await message.delete()
        #print('Deleted message')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
      print(f'{member.guild.id} : {before.channel} | {after.channel}')
      role1 = member.guild.get_role(905657181792247810)
      if member.guild.id == 468176956232302603:
        if after.channel == None:
          await member.remove_roles(role1, reason='Left the VC.') 
          #await self.log0101(f'<@{member.id}> : {before.channel}>{after.channel}, removed  VC role')
        else:
          if after.channel != None and before.channel == None:
            await member.add_roles(role1, reason='Joined the VC.')
            #await self.log0101(f'<@{member.id}> : {before.channel}>{after.channel}, added VC role')

    
    # Joining server stuff
    @commands.Cog.listener()
    async def on_member_join(self, member):
      if location == 0:
        print(f'{member.name} joined the server. Skipping welcome messages.')
        return
      # Send them an intro message and talk about verification
      memberdm = await member.create_dm()
      await memberdm.send(f"""Hey there, <@{member.id}>! 
## Welcome to the official Ninja.io Discord.
We look forward to welcoming you soon! To prevent alt accounts from joining, we require 2 things:
- Verification via <@703886990948565003>, so check your dms with that bot. If you fail to verify, you will be kicked.
- That you have an email verified with Discord, and wait 10 minutes before you can chat in the server.
*If you need help verifying your email, please follow this guide: https://support.discordapp.com/hc/en-us/articles/213219267-Resending-Verification-Email*
I'll be back in **10 minutes** to let you know that the timer has ended! Be sure to verify in the meantime!
After that, you can check out the following channels:
    <#670362003356778498> - See the latest announcements from the Ninja.io developer
    <#670361959345946657> - Read the Rules!!!
    <#750176588418646096> or <#834228209305387038> - See some amazing art made by the community!
If you get kicked or just leave and ever want to rejoin us, you may use this link: https://discord.gg/yAYmSWZ \n--""")
      # Wait 10 minutes
      await asyncio.sleep(630) # Set to 30 seconds for testing. 10 minutes is 600 seconds
      # Check if they are still in the server
      if member in member.guild.members:
        # DM them that their timeout has ended
        await member.send('## Yay! You can now chat in the Ninja.io server!\nPlease join us by saying hi in <#670362292659159040>. You will also be pinged there shortly!')
        # Wait 10 seconds
        await asyncio.sleep(10)
        # Remove their temp verify role if they have it
        role1 = member.guild.get_role(1206992415047819295)
        try:
          await member.remove_roles(role1, reason='Verification ended.')
        except Exception as e:
          print(f'Error removing role: {e}')
        # Ping them in general chat
        channel = member.guild.get_channel(670362292659159040)
        await channel.send(f'Welcome, <@{member.id}> as the {member.guild.member_count}th user!')
        await channel.send(f'~{randomtopic()}') 
      # If they left the server, just print to console
      else:
        print(f'{member.name} left/kicked before verification ended.')


    #commands
    @commands.command(aliases=['ins', 'inspireme'], help='Inspires!')
    async def inspire(self, ctx):
      embed = Embed(color=Color.magenta(), description=get_quote())
      await ctx.send(embed=embed)

    @commands.command(name='count', help='Count the characters in a message')
    @commands.cooldown(1, 60)
    async def count(self, ctx, *, msg):
      count = len(msg)
      if count == 0:
        await ctx.send('Nothing to count.')
      else:
        await ctx.send('Count: %s'%(str(count)))
        
    @count.error
    async def count_error(self, ctx, error):
      await ctx.send(f'Error: {error}', delete_after=15)


    @commands.command(help='Ping Giveaways')
    @commands.cooldown(1, 60)
    async def gwping(self, ctx):
      print(ctx.channel.id)
      if ctx.channel.id == 790771344597188658:
        await ctx.send(f'<@&790775742760878110> **Giveaway!** \nGiven by <@{ctx.author.id}>')
        await ctx.message.delete()
      else:
        await ctx.send('Bruh. Go to <#790771344597188658> and run this command smh')
        
    @gwping.error
    async def gwping_error(self, ctx, error):
      await ctx.send(f'Error: {error}', delete_after=15)


    @commands.command(help='Get a list of roles from the server', aliases=['rl'])
    @commands.cooldown(3, 30, commands.BucketType.channel)
    async def role_list(self, ctx):
      ch = ctx.guild
      title = 'List of roles in ninja.io discord: \n'
      message = ''
      message2 = ''
      roles = ch.roles
      for rl in roles:
        roleline = f'{rl.mention} : {rl.color}\n'
        if len(message) + len(title) + len(roleline) < 2000:
          message += roleline
        else: 
          message2 += roleline
      embed = Embed(color = Color.green(), title=title, description=message)
      await ctx.send(embed=embed)
      if len(message2) > 0:
        embed2 = Embed(color = Color.green(), description=message2)
        await ctx.send(embed=embed2)
    

    @commands.command(help='Add your own autoreaction when you are pinged.')
    @commands.has_any_role(845734135922163762, 470547452873932806, 670427731468746783)
    async def claim(self, ctx, emoji):
      trigger = f'{ctx.author.id}'
      print(f'{emoji}:{trigger}')
      try: 
        await ctx.message.add_reaction(emoji)
        if emoji == "⭐":
          raise Exception("⭐ is not allowed.")
      except Exception as e:
        await ctx.send(f"That is not a valid emoji. Emojis must be from this server. \nError: {e}", delete_after=15) 
        return
      #db['newreacts'] = dab
      emojireacts = {}
      curr.execute('SELECT * FROM reactions')
      for row in curr.fetchall():
        emojireacts[row[1]] = row[2]
      if trigger in emojireacts:
        #print(f"{trigger} - {emoji}")
        curr.execute('UPDATE reactions SET eid=%s WHERE trigger = %s', (str(emoji), str(trigger)))
        await ctx.send(f'The emoji for <@{trigger}> has been updated to {emoji}.')
      else:
        curr.execute('INSERT INTO reactions(trigger, eid) VALUES (%s, %s)', (str(trigger), str(emoji)))
        await ctx.send(f'{emoji} added to react when <@{trigger}> is mentioned.')
      conn.commit()
    
    @claim.error
    async def claim_error(self, ctx, error):
      await ctx.send(f'Error: {error}', delete_after=15)


async def setup(bot):
  await bot.add_cog(Misc(bot))
