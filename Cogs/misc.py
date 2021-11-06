import discord, os, sys, json, random, logging, requests, datetime
from discord.ext import commands
from discord import Embed, Color

def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  print(str(json_data))
  quote = json_data[0]['q'] + """ 
  *""" + json_data[0]['a'] + "*"
  return(quote)

class Misc(commands.Cog):

    def __init__(self, bot):
      self.bot = bot

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
      if message.channel.id == 835164179001901099:
        check = False
        for i in [470547452873932806, 670427731468746783]:
          role = message.guild.get_role(i)
          #print(role)
          #print(message.author.roles)
          if role in message.author.roles:
            #pass
            check = True
        if check != True and message.attachments == []:
          await message.author.send(f'Your message in <#{message.channel.id}> was deleted because it did not have an attachment. \nHere\'s the message for referance: {message.content}')
          await self.log0101(message=f'<@{message.author.id}> in <#{message.channel.id}> : {message.content}', title=f'Deleted message')
          await message.delete()
          #print('Deleted message')



    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
      print(f'{member.guild.id} : {before.channel} | {after.channel}')
      role1 = member.guild.get_role(905657181792247810)
      if member.guild.id == 468176956232302603:
        if after.channel == None:
          await member.remove_roles(role1, reason='Left the VC.') 
          await self.log0101(f'<@{member.id}> : {before.channel}>{after.channel}, removed  VC role')
        else:
          if after.channel != None and before.channel == None:
            await member.add_roles(role1, reason='Joined the VC.')
            await self.log0101(f'<@{member.id}> : {before.channel}>{after.channel}, added VC role')
            


    #commands
    @commands.command(aliases=['ins', 'inspireme'], help='Inspires!')
    async def inspire(self, ctx):
      embed = Embed(color=Color.magenta(), description=get_quote())
      await ctx.send(embed=embed)

    @commands.command(name='count', help='Count the characters in a message')
    @commands.cooldown(1, 60)
    async def count(self, ctx, *, msgd):
      count = len(msgd)
      if count == 0:
        await ctx.send('Nothing to count.')
      else:
        await ctx.send('Count: %s'%(str(count)))
        
    @count.error
    async def count_error(self, ctx, error):
      await ctx.send(f'Error: {error}', delete_after=15)


    @commands.command(help='pingpong', aliases=['pong'])
    async def ping(self, ctx):
      await ctx.send(f':ping_pong:  {round(self.bot.latency *1000)}ms!')


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

def setup(bot):
  bot.add_cog(Misc(bot))
