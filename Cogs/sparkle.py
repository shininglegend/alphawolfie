import discord, os, sys, json, random, logging
from discord.errors import Forbidden
from discord.ext import commands
#from replit import db
from discord import Embed, Color
#import sqlite3
import psycopg2 as pgsql

conn = pgsql.connect("dbname=alphawolfie user=postgres password=password")
#con = sqlite3.connect('/root/data/data1.db')
#con = sqlite3.connect('data1.db')

emoji = 918630874898120705
#cur = con.cursor()
curr = conn.cursor()
#print('I updated')



#cur.execute("CREATE TABLE IF NOT EXISTS sparklescores(id INTEGER PRIMARY KEY AUTOINCREMENT, guild INTEGER, userid INTEGER, score INTEGER DEFAULT 0)")
#cur.execute("CREATE TABLE IF NOT EXISTS sparklesettings(id INTEGER PRIMARY KEY AUTOINCREMENT, guild INTEGER, emoji INTEGER)")
#cur.execute("CREATE TABLE IF NOT EXISTS sparklechannels(id INTEGER PRIMARY KEY AUTOINCREMENT, guild INTEGER, channel INTEGER, minScore INTEGER, maxScore INTEGER)")
#0 id
#1 guild
#2 channel
#3 minscore
#4 maxscore
#con.commit()



#Custom checks
def is_it_me(ctx):
    return ctx.message.author.id == 585991293377839114

def addGuild(guild, emoji1):
  g = None
  curr.execute('SELECT * FROM sparklesettings WHERE guild = %s', (guild,))
  for row in curr:
    g = row
  if not g:
    curr.execute('INSERT INTO sparklesettings (guild, emoji) VALUES (%s, %s)', (guild, emoji1))
    conn.commit()

def getEmote(guild):
  g = None
  curr.execute('SELECT * FROM sparklesettings WHERE guild = %s', (guild,))
  for row in curr:
    g = row[2]
  if not g:
    g = emoji
  return g

def chaUpdate(guild,  channel, minScore=5, maxScore=10):
  g = None
  curr.execute('SELECT * FROM sparklechannels WHERE guild = %s AND channel = %s', (guild, channel))
  for row in curr:
    g = row
  print(g)
  if g == None:
    curr.execute('INSERT INTO sparklechannels (guild, channel, minScore, maxScore) VALUES (%s, %s, %s, %s)', (guild, channel, minScore, maxScore))
    print('added channel')
    conn.commit()
  else:
    curr.execute('UPDATE sparklechannels SET minScore = %s, maxScore = %s WHERE channel = %s AND guild = %s', (minScore, maxScore, channel, guild))
    print('updated channel')
    conn.commit()

def chaDel(guild,  channel):
  curr.execute('DELETE FROM sparklechannels WHERE guild = %s AND channel = %s', (guild, channel))
  conn.commit()

def chatChannels():
  g = []
  curr.execute('SELECT * FROM sparklechannels')
  for row in curr:
    #print(row)
    g.append(row[2])
    #returns a list of the rows 
  return list(g)

def allChannels():
  curr.execute('SELECT * FROM sparklechannels')
  g = curr.fetchall()
  #returns a list of tuples!
  return g

def getChannel(channel, guild):
  g = ()
  curr.execute('SELECT * FROM sparklechannels WHERE guild = %s and channel = %s', (guild, channel))
  for row in curr:
    g=row 
  #print(g)
  return g

def checkScore(userid, guildid):
  scorefetched = None
  curr.execute('SELECT * FROM sparklescores WHERE userid = %s AND guild = %s', (userid, guildid))
  for row in curr:
    scorefetched = row
  
  if scorefetched != None:
    #print('User found in db')
    return str(scorefetched[3])
  else:
    print('User not found.')
    return '0'

def changeScore(userid, guildid, amount=1):
  #curr.execute('INSERT INTO sparklescores (userid, guild, score) VALUES (%s, %s, %s)', (userid, guildid, amount))
  #conn.commit()
  scorefetched = None
  curr.execute('SELECT * FROM sparklescores WHERE userid = %s AND guild = %s', (userid, guildid))
  for row in curr:
    scorefetched = row
  if scorefetched == None:
    curr.execute('INSERT INTO sparklescores (userid, guild, score) VALUES (%s, %s, %s)', (userid, guildid, amount))
    print(f'User got {str(amount)} point(s). {userid}')
    score = amount
  elif scorefetched[3] + amount < 0:
    print('Ignoring negitive score. User database has not been changed.')
    score = scorefetched[3]
  else:
    score = amount + scorefetched[3]
    curr.execute('UPDATE sparklescores SET score = %s WHERE userid = %s AND guild = %s ', (score, userid, guildid))
    print(f'User got {str(amount)} point(s).  New score is {score}. {userid}')
  conn.commit()
  return score

def removeGld(guildid):
  curr.execute('DELETE FROM sparklescores WHERE guild = %s', (guildid,))
  conn.commit()

def guildScores(guildid):
  print(type(guildid))
  gscores = {}
  curr.execute('SELECT * FROM sparklescores WHERE guild = %s ORDER BY score DESC', (guildid,))
  for row in curr:
    #print(row)
    gscores[row[2]] = row[3]
  #print(gscores)
  return gscores 

'''def chatChannels():
  cha = open(chaFilename, "r")
  cha1 = cha.read()
  cha.close()
  channels = cha1.split(':')
  channels = list(map(int, channels))
  return channels'''

def validMsg(message):
  if ' ' in message or len(message) > 4:
    return True
  else:
    return False



class Snowball(commands.Cog):
    def __init__(self, bot):
      self.bot = bot
      self.description = 'Spawn cool stuff!'
      self.chatA = {}
      self.chatTar = {}
      self.Twait = {}
      for cha in allChannels():
        #print(cha)
        cha1 = cha[2]
        self.chatA[cha1] = 0
        self.chatTar[cha1] = random.randint(cha[3], cha[4])
        self.Twait[cha1] = False
      self.chatChannels = chatChannels()
      print(self.chatTar)

    #events
    @commands.Cog.listener()
    async def on_ready(self):
      print('Snowball is online')
    
    @commands.Cog.listener()
    async def on_message(self, message):
      #await self.bot.process_commands(message)
      if message.author.id == self.bot.user.id:
        return
      mesCha = message.channel.id
      #check if channel is in db
      self.chatChannels = chatChannels()
      #print(self.chatChannels)
      if mesCha in self.chatChannels and validMsg(message.content):
        self.chatA[mesCha] = self.chatA[mesCha] + 1
        print(f'Msg seen. {self.chatTar[mesCha] - self.chatA[mesCha]} left. a:{self.chatA[mesCha]} t:{self.chatTar[mesCha]}', end='')  
        #check if there is a sparkle already spawned
        if any([self.Twait[mesCha] == False, self.chatTar[mesCha] - self.chatA[mesCha] < -5]): 
          #check if chat activity is exceeded
          if self.chatA[mesCha] > self.chatTar[mesCha]:
            self.Twait[mesCha] = True 
            print('Target Triggered')
            Temoji = self.bot.get_emoji(getEmote(message.guild.id)) 
            responses = [f'**The snow gathers... And a {Temoji} appears!**',
              f'**{Temoji}. No more needs to be said.**',
              f'**Discord drops off a {Temoji}!**',
              f'**Hiii! \nDid you know about the {Temoji}?**',
              f'**You are gifted one {Temoji}. Claim it quick!**',
              f'**Ara Ara! This {Temoji} probaly has bad luck now.**',]
            Tmessage = await message.channel.send(random.choice(responses))
            def check(reaction, user):
              return str(reaction.emoji) == str(Temoji) and reaction.message == Tmessage
            print('Sent reaction')
            await Tmessage.add_reaction(Temoji)
            while True:
              try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=200.0, check=check)
              except TimeoutError:
                await Tmessage.edit(content=f'This {Temoji} didn\'t get claimed!', delete_after=5)
                self.chatA[mesCha] = 0 
                cha = getChannel(mesCha, message.guild.id)
                self.chatTar[mesCha] = random.randint(cha[3], cha[4])
                print(self.chatTar[mesCha] + 1)
                self.Twait[mesCha] = False
                break
              if user.id == self.bot.user.id:
                print('Bot reaction ignored')
                #pass
              else:
                print('reaction seen')
                await Tmessage.clear_reaction(Temoji)
                guildid = user.guild.id
                i = random.randint(0, 75)
                print(i)
                if i in [10, 20, 21]:
                  print('lost a point')
                  changeScore(user.id, guildid, -1)
                  await Tmessage.edit(content=f'**{Temoji} froze to the hand of <@{user.id}> and they lost a point!**', delete_after=7)
                elif i in [5, 45, 46]:
                  print('double points')
                  changeScore(user.id, guildid, 2)
                  await Tmessage.edit(content=f'**<@{user.id}> found a epic, perfect {Temoji} gained 2 points!**', delete_after=7)
                elif i in [25, 30, 35, 40, 41, 42, 43]:
                  print('nothing')
                  await Tmessage.edit(content=f'**<@{user.id}>\'s {Temoji} crumbles. They gain no points**', delete_after=7)
                else:
                  print('normal')
                  changeScore(user.id, guildid)
                  responses = [f'**{Temoji} has been claimed by <@{user.id}>!**',
                    f'**<@{user.id}> jumps to the front to claim the {Temoji}!**',
                    f'**<@{user.id}> slides in and grabs the {Temoji}!**',
                    f'**You were about to grab the {Temoji}, but... <@{user.id}> got there first!**',
                    f'**A random <@{user.id}> appears and snatches the {Temoji}!**',
                    f'**<@{user.id}> uses the power of flash and claims the {Temoji}!**']
                  await Tmessage.edit(content=random.choice(responses), delete_after=7)
                #Tmessage = Nones
                self.chatA[mesCha] = 0
                cha = getChannel(mesCha, message.guild.id)
                #print(cha)
                self.chatTar[mesCha] = random.randint(cha[3], cha[4])
                self.Twait[mesCha] = False
                print(self.chatTar[mesCha] + 1)
                break
              
    @commands.command(help='Check your score', aliases=['bal', 'sparkles'])
    async def balance(self, ctx, user:discord.Member=None):
      if not user:
        user = ctx.message.author
      guildid = ctx.guild.id
      m = checkScore(user.id, guildid)
      Temoji = self.bot.get_emoji(getEmote(ctx.guild.id))  
      msg = f'__{user.display_name}__ has {m}  {Temoji}!'
      embed = Embed(color=Color.green(), title=msg)
      await ctx.reply(embed=embed)

    @commands.command(help='View the leaderboard', aliases=['lb'])
    async def leaderboard(self, ctx):
      await ctx.channel.typing()
      guildid = ctx.guild.id
      lbid = guildScores(guildid)
      #print(lbid)
      lbid1 = list(lbid.keys())
      if len(lbid1) > 9:
        top10 = lbid1[:10]
      else:
        top10 = lbid1[:len(lbid1)]
      #print(top10)
      Temoji = self.bot.get_emoji(getEmote(ctx.guild.id))  
      def CreateLb(current10, cPos): #current10 is the dict set of current id+score, cPos is the position of those ids
        cembed = discord.Embed(color=Color.green(), title=f'{ctx.guild.name} {Temoji} Leaderboard:')
        cembed.set_footer(text=f'Requested by: {ctx.author.name}#{ctx.author.discriminator}')
        #print(current10)
        for uid in current10:
          print(uid)
          cPos+=1
          uscore = lbid[uid]
          umember = ctx.guild.get_member(int(uid))
          #print(umember)
          if not umember == None: 
            names = f'{cPos}: {umember.name}#{umember.discriminator}'
          else:
            names = f'{cPos}: Missing User#0000'
          uscore = f'  {Temoji} `{uscore}`'
          cembed.add_field(name=names, value=uscore, inline=False)
        return cembed
      currentpos = 1
      #send the first message
      messagel = await ctx.send(embed=CreateLb(top10, 0))
      #await ctx.message.delete()
      def check(reaction, user):
        return str(reaction.emoji) == "▶️" or str(reaction.emoji) == "◀️" and user.id == ctx.author.id and reaction.message.id == messagel.id
      while True:
        try:
          await messagel.add_reaction("◀️")
          await messagel.add_reaction("▶️")
          reaction, user = await self.bot.wait_for('reaction_add', timeout=120.0, check=check)
        except Exception:
          break
        if str(reaction.emoji) == "◀️" and user.id == ctx.author.id:
          #move back
          await messagel.remove_reaction("◀️",user)
          #check if maxed out
          if currentpos <= 1:
            pass
          else:
            currentpos-=1 
            #deal with short leaderboards
            if len(lbid) > (currentpos*10):
              current10 = lbid1[(currentpos*10-9):]
            #deal with 10 leaderboards
            if len(lbid) > (currentpos*10):
              current10 = lbid1[(currentpos*10-10):(currentpos*10)]
            await messagel.edit(embed=CreateLb(current10, ((currentpos*10)-10)))
        if str(reaction.emoji) == "▶️" and user.id == ctx.author.id:
          #move forward
          await messagel.remove_reaction("▶️",user)
          #check if maxed out
          if len(lbid) <= (currentpos*10):
            pass
          else:
            currentpos+=1 
            #deal with short leaderboards
            if len(lbid) > (currentpos*10):
              current10 = lbid1[(currentpos*10-10):]
            #deal with 10 leaderboards
            if len(lbid) > (currentpos*10):
              current10 = lbid1[(currentpos*10-10):(currentpos*10)]
            await messagel.edit(embed=CreateLb(current10, ((currentpos*10)-10)))
  
    @commands.command(help='Show which channels spawn sparkles, and the values for those channels!')
    async def sChaList(self, ctx):
      Temoji = self.bot.get_emoji(getEmote(ctx.guild.id))  
      embed = discord.Embed(color=Color.green(), title=f'{Temoji} will spawn in these channels:')
      pos = 0
      channelids = ctx.guild.channels
      chaids = []
      for channelid in channelids:
        chaids.append(str(channelid.id))
      #print(chaids)
      chatChannel = chatChannels()
      allChannel = allChannels()
      print(allChannel)
      for channel in chatChannel:
        currCha = allChannel[pos]
        if str(channel) in chaids:
          pos+=1
          embed.add_field(name=pos, value=f'<#{channel}>: {currCha[3]-1}-{currCha[4]-1}', inline=False)
      await ctx.reply(embed=embed)
    
    @commands.command(help='Stop a channel from spawning. Admin only', aliases=['sChaDel'])
    @commands.has_guild_permissions(administrator=True)
    async def sChaRemove(self, ctx, cha:discord.TextChannel):
      Temoji = self.bot.get_emoji(getEmote(ctx.guild.id))  
      i = chatChannels()
      print(i)
      cha = cha.id
      if int(cha) in i:
        chaDel(ctx.guild.id, cha)
        self.chatChannels = chatChannels()
        await ctx.reply(f'Done. <#{cha}> will no longer spawn {Temoji}.')
      else:
        await ctx.reply('That channel was not found')

    @commands.command(help='Start spawning in a channel. Admin only')
    @commands.has_guild_permissions(administrator=True)
    async def sChaAdd(self, ctx, cha:discord.TextChannel, minScore=5, maxScore=10):
      Temoji = self.bot.get_emoji(getEmote(ctx.guild.id))
      try:
        b = await cha.send('This is a test message. You can safely ignore it.', delete_after=3)
        await b.add_reaction('✔')
      except Forbidden:
        await ctx.send(f'That channel is not in this server, or I do not have the required permissions to spawn {Temoji} in that channel.')
      i = chatChannels()
      cha = cha.id
      if int(cha) not in i:
        chaUpdate(ctx.guild.id, cha, int(minScore), int(maxScore))
        self.chatChannels = chatChannels()
        mesCha = cha
        self.chatA[mesCha] = 0
        cha2 = getChannel(mesCha, ctx.guild.id)
        #print(cha)
        self.chatTar[mesCha] = random.randint(cha2[3], cha2[4])
        self.Twait[mesCha] = False
        print(self.chatTar[mesCha] + 1)
        await ctx.reply(f'Done. <#{cha}> will now spawn {Temoji}.')
      else:
        await ctx.reply(f'That channel is already spawning {Temoji}!')

    @commands.command(help='Update the spawnrate. Admin only', aliases=['sChaUp'])
    @commands.has_guild_permissions(administrator=True)
    async def sChannelUpdate(self, ctx, cha:discord.TextChannel, minScore=5, maxScore=10):
      Temoji = self.bot.get_emoji(getEmote(ctx.guild.id))
      i = chatChannels()
      cha = cha.id
      if int(cha) in i:
        chaUpdate(ctx.guild.id, cha, int(minScore), int(maxScore))
        mesCha = cha
        cha2 = getChannel(mesCha, ctx.guild.id)
        #print(cha)
        self.chatA[mesCha] = 0
        self.chatTar[mesCha] = random.randint(cha2[3], cha2[4])
        await ctx.reply(f'Done. <#{cha}> will now spawn {Temoji} randomly every {minScore-1} - {maxScore-1} messages.')
      else:
        await ctx.reply(f'That channel isn\'t spawning {Temoji}!')
        
    
    @commands.command(help='Send a backup of the database')
    @commands.check(is_it_me)
    async def sBackup(self, ctx):
      guildid = ctx.guild.id
      i = guildScores(guildid)
      embed = discord.Embed(color=Color.green(), title='Current user database for this guild:', description=str(i))
      await ctx.send(embed=embed)

    @commands.command(help='Fix Sparkles if they aren\'t working, Admin only')
    @commands.has_guild_permissions(administrator=True)
    async def sReClear(self, ctx):
      global conn, curr
      conn.close()
      conn = pgsql.connect("dbname=alphawolfie user=postgres password=password")
      curr = conn.cursor()
      self.chatA = {}
      self.chatTar = {}
      self.Twait = {}
      allcha = allChannels()     
      for cha in allcha:
        self.chatA[cha[2]] = 0
        self.chatTar[cha[2]] = random.randint(cha[2], cha[3])
        self.Twait[cha[2]] = False
      self.chatChannels = chatChannels()
      print(self.chatTar)
      embed = discord.Embed(color=Color.green(), title='Current variable status')
      embed.add_field(name='List of channels fetched:', value=allcha)
      embed.add_field(name='Waiting for a sparkle to be claimed:', value=self.Twait)
      embed.add_field(name='Messages counted:', value=self.chatA)
      embed.add_field(name='Target messages before spawn:', value=self.chatTar)
      await ctx.send(content='<@585991293377839114>', embed=embed)
      await ctx.send('Done. Hope that works!')
    
    @commands.command(help='Reset the sparkle scores for this server.')
    @commands.check(is_it_me)
    async def sReset(self, ctx):
      guildid = ctx.guild.id
      dev = self.bot.get_user(585991293377839114)
      i = guildScores(guildid)
      embed = discord.Embed(color=Color.green(), title='Current user database', description=str(i))
      await dev.send(embed=embed)
      removeGld(guildid)
      embed2 = discord.Embed(color=Color.green(), title='Database has been cleared. Its a new dawn!')
      await ctx.send(embed=embed2)
      await ctx.message.delete()

    @commands.command(help='Check bot status, Dev only')
    @commands.check(is_it_me)
    async def sCheck(self, ctx):
      embed = discord.Embed(color=Color.green(), title='Current variable status')
      embed.add_field(name='Waiting for a sparkle to be claimed:', value=self.Twait)
      embed.add_field(name='Messages counted:', value=self.chatA)
      embed.add_field(name='Target messages before spawn:', value=self.chatTar)
      await ctx.send(embed=embed)
      

    
async def setup(bot):
  await bot.add_cog(Snowball(bot))