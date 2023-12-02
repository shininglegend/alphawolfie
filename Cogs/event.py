import discord, os, sys, json, random, logging, ast
from discord.errors import Forbidden
from discord.ext import commands
#from replit import db
from discord import Embed, Color, app_commands
#import sqlite3
import psycopg2 as pgsql

from init import conn, curr, is_it_me, location


# This defines the emoji to use. I should really have this in a database, but I'm too lazy to do that right now. :P
emoji = 1180455748673740831
emojiName = 'snowballs'
#cur = con.cursor()
#print('I updated')
userid = None
response_after = ['**USER, like a swift winter breeze, gracefully seizes the EMOJI in mid-flight.**',
    '**As silent as falling snow, USER ensnares the EMOJI with expert precision.**',
    '**With the agility of a snow fox, USER outwits the EMOJI, capturing it deftly.**',
    '**Like a samurai\'s blade in moonlight, USER swiftly intercepts the EMOJI.**',
    '**USER, embodying the spirit of winter, masterfully catches the EMOJI.**',
    '**In a dance as elegant as snowflakes, USER elegantly clasps the EMOJI.**',
    '**With the patience of a frozen lake, USER waits before snatching the EMOJI.**',
    '**USER, with the stealth of a shadow on snow, captures the EMOJI unawares.**',
    '**Like a crane amidst a snowy meadow, USER gracefully snatches the EMOJI.**',
    '**With movements as fluid as a winter stream, USER secures the EMOJI.**',
    '**USER, reflecting the stillness of a winter night, calmly catches the EMOJI.**',
    '**As if guided by the stars, USER\'s hand finds the EMOJI in the cold air.**',
    '**With a touch as gentle as snowfall, USER claims the EMOJI.**',
    '**USER, mimicking the quiet of a snow-covered forest, stealthily catches the EMOJI.**',
    '**Like a mountain standing firm against the winter wind, USER grasps the EMOJI.**',
    '**USER, channeling the endurance of winter, triumphantly captures the EMOJI.**',
    '**In a moment as fleeting as a snowflake\'s touch, USER seizes the EMOJI.**',
    '**With the wisdom of winter nights, USER skillfully intercepts the EMOJI.**',
    '**USER, as if part of a winter\'s tale, heroically catches the EMOJI.**',
    '**Like a haiku, simple yet profound, USER captures the essence of the EMOJI.**',
    '**USER, with the harmony of a snow-laden branch, gently catches the EMOJI.**',
    '**In an echo of ancient winter legends, USER adeptly secures the EMOJI.**',
    '**USER, as timeless as winter\'s embrace, effortlessly ensnares the EMOJI.**',
    '**With the serenity of a snow-globe scene, USER gracefully catches the EMOJI.**',
    '**USER, evoking the mystery of a snowy twilight, masterfully captures the EMOJI.**'
  ]

response_before = [
    '**The EMOJI, a frosty orb, glistens like a crystal under the morning sun.**',
    '**Amidst the winter silence, the EMOJI sits, a lone sentinel in the snow.**',
    '**Like a pearl in the sea of white, the EMOJI catches the faint light of dawn.**',
    '**The EMOJI, dusted with frost, holds the whispers of the winter wind.**',
    '**In the pale moonlight, the EMOJI shimmers with an ethereal glow.**',
    '**The EMOJI, carved by the chill, stands as a monument to fleeting moments.**',
    '**As if kissed by winter fairies, the EMOJI sparkles with a delicate frost.**',
    '**The EMOJI, nestled in the embrace of winter, wears a cloak of powdered snow.**',
    '**Like a forgotten dream, the EMOJI rests, ethereal and untouched in the morning light.**',
    '**The EMOJI, a solitary figure, mirrors the solemnity of the winter\'s sky.**',
    '**Beneath the twilight stars, the EMOJI glows softly, a beacon of night\'s magic.**',
    '**The EMOJI, veiled in mist, stands as a guardian of winter\'s secrets.**',
    '**In the hush of the snowy forest, the EMOJI remains a silent observer.**',
    '**The EMOJI, a testament to winter\'s craft, lies sculpted by the playful wind.**',
    '**Like a droplet from a winter cloud, the EMOJI sits, pure and simple.**',
    '**The EMOJI, a frozen echo, resonates with the stillness of the winter valley.**',
    '**Amidst the dance of falling snowflakes, the EMOJI stands, proud and serene.**',
    '**The EMOJI, like a whispered riddle, holds the mysteries of the frost.**',
    '**In the embrace of the cold, the EMOJI gleams, a relic of winter\'s grace.**',
    '**The EMOJI, a solitary jewel, reflects the solemn beauty of the winter night.**',
    '**As the world sleeps under the winter sky, the EMOJI dreams in the snow.**',
    '**The EMOJI, touched by the dawn, wears a crown of sunlit ice.**',
    '**In the quiet of the snowy meadow, the EMOJI is a testament to winter\'s art.**',
    '**The EMOJI, like a brushstroke on a white canvas, lies in perfect harmony.**',
    '**As if part of an ancient winter fable, the EMOJI rests, timeless and profound.**'
]




#curr.execute("CREATE TABLE IF NOT EXISTS sparklescores(id INTEGER PRIMARY KEY AUTOINCREMENT, guild INTEGER, userid INTEGER, score INTEGER DEFAULT 0)")
#curr.execute("CREATE TABLE IF NOT EXISTS sparklesettings(id INTEGER PRIMARY KEY AUTOINCREMENT, guild INTEGER, emoji INTEGER)")
#curr.execute("CREATE TABLE IF NOT EXISTS sparklechannels(id INTEGER PRIMARY KEY AUTOINCREMENT, guild INTEGER, channel INTEGER, minScore INTEGER, maxScore INTEGER)")
#0 id
#1 guild
#2 channel
#3 minscore
#4 maxscore
# conn.commit()

def notGeneral(ctx):
  return not(any([ctx.channel.id == 670362292659159040, ctx.channel.id == 774408820721844254]))

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
    # Fetch the current score for the user and guild
    curr.execute('SELECT score FROM sparklescores WHERE userid = %s AND guild = %s', (userid, guildid))
    row = curr.fetchone()

    # Determine the new score based on the current score and amount
    if row:
        current_score = row[0]
        # If the new score would be negative, keep the current score
        if current_score + amount < 0:
            print('Ignoring negative score. User database has not been changed.')
            return current_score
        # Otherwise, update the score
        else:
            new_score = current_score + amount
            curr.execute('UPDATE sparklescores SET score = %s WHERE userid = %s AND guild = %s', (new_score, userid, guildid))
            print(f'User got {amount} point(s). New score is {new_score}. {userid}')
            conn.commit()
            return new_score
    # If the user doesn't exist, insert a new record with the given amount
    else:
        curr.execute('INSERT INTO sparklescores (userid, guild, score) VALUES (%s, %s, %s)', (userid, guildid, amount))
        print(f'User got {amount} point(s). {userid}')
        conn.commit()
        return amount

def removeGld(guildid):
  curr.execute('DELETE FROM sparklescores WHERE guild = %s', (guildid,))
  conn.commit()

def guildScores(guildid):
    gscores = {}
    query = 'SELECT userid, score FROM sparklescores WHERE guild = %s ORDER BY score DESC'
    curr.execute(query, (guildid,))
    gscores = {row[0]: row[1] for row in curr.fetchall()}
    return gscores

'''def chatChannels():
  cha = open(chaFilename, "r")
  cha1 = cha.read()
  cha.close()
  channels = cha1.split(':')
  channels = list(map(int, channels))
  return channels'''

def validMsg(message):
  if ' ' in message or len(message) > 5:
    return True
  else:
    return False



class Event(commands.Cog):
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
      print('Events is online')
    

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
            # Format the response
            response_msg = random.choice(response_before).replace("EMOJI", str(Temoji))
            Tmessage = await message.channel.send(response_msg)
            # Process after the message is sent
            antiautoclicker = random.randint(1, 10)
            if antiautoclicker <= 1:
              extramsg = await message.channel.send(f'Bonus message to mess up you autoclickers!\nGo do something else for a bit.\nYou\'re too obbsessed with {Temoji}!', delete_after=3)
              await extramsg.add_reaction(Temoji)
            elif antiautoclicker <= 3:
              await Tmessage.add_reaction('👀')
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
                  await Tmessage.edit(content=f'**{Temoji} melted due to <@{user.id}> being bad instead of good this year!**', delete_after=7)
                elif i in [5, 45, 46]:
                  print('double points')
                  changeScore(user.id, guildid, 2)
                  await Tmessage.edit(content=f'**<@{user.id}> is Santa\'s favorite, and got a perfect {Temoji} gaining 2 points!**', delete_after=7)
                elif i in [25, 30, 35, 40, 41, 42, 43]:
                  print('nothing')
                  await Tmessage.edit(content=f'**<@{user.id}>\'s {Temoji} was an illusion. They gain no points**', delete_after=7)
                else:
                  print('normal')
                  changeScore(user.id, guildid)
                  response_msg = random.choice(response_after).replace("EMOJI", str(Temoji))
                  response_msg = response_msg.replace("USER", f'<@{user.id}>')
                  await Tmessage.edit(content=response_msg, delete_after=7)
                #Tmessage = Nones
                self.chatA[mesCha] = 0
                cha = getChannel(mesCha, message.guild.id)
                #print(cha)
                self.chatTar[mesCha] = random.randint(cha[3], cha[4])
                self.Twait[mesCha] = False
                print(self.chatTar[mesCha] + 1)
                break
              

    @commands.hybrid_command(help='Check your score', aliases=['bal', emojiName])
    @commands.check(notGeneral)
    async def balance(self, ctx, user:discord.Member=None):
      await ctx.defer()
      if not user:
        user = ctx.message.author
      guildid = ctx.guild.id
      m = checkScore(user.id, guildid)
      Temoji = self.bot.get_emoji(getEmote(ctx.guild.id))  
      msg = f'__{user.display_name}__ has {m}  {Temoji}!'
      embed = Embed(color=Color.green(), title=msg)
      await ctx.send(embed=embed)


    @app_commands.command(description=f'Spawn a {emojiName} on demand.')
    async def spawn(self, interaction: discord.Interaction) -> None:
      await interaction.response.send_message("No. Why would I possibly let you cheat?!", ephemeral=True)
      await interaction.guild.get_channel(903139993646682113).send(f'<@{interaction.user.id}> tried to spawn a {emojiName} on demand! Bored?')


    @commands.command(help='View the leaderboard', aliases=['lb'])
    @commands.check(notGeneral)
    async def leaderboard(self, ctx, guild_score=None):
      await ctx.channel.typing()
      
      # If no guild_score provided, fetch the leaderboard data from the database
      if guild_score is None:
          guild_id = ctx.guild.id
          leaderboard_data = guildScores(guild_id)
          leaderboard_keys = list(leaderboard_data.keys())
      else:
          # Parsing the string into a dictionary
          try:
            given_leaderboard_data = ast.literal_eval(guild_score)
          except ValueError:
            await ctx.send('Invalid leaderboard data provided.')
            return
          guild_id = ctx.guild.id
          current_leaderboard_data = guildScores(guild_id)

          # Compute the differences between the given scores and current scores
          leaderboard_data = {user_id: current_leaderboard_data.get(user_id, 0) - given_score
                              for user_id, given_score in given_leaderboard_data.items()
                              if given_score != current_leaderboard_data.get(user_id, 0)}
          
          # Sort leaderboard_keys by the new scores in descending order
          leaderboard_keys = list(leaderboard_data.keys())
          leaderboard_keys.sort(key=lambda user_id: leaderboard_data[user_id], reverse=True)

          await ctx.send('This leaderboard is a temporary event leaderboard. Please use the command without any arguments to get the current leaderboard.')

      T_emoji = self.bot.get_emoji(getEmote(ctx.guild.id))


      # Function to create leaderboard embed
      def create_leaderboard_embed(current_keys, start_pos):
          embed = discord.Embed(color=Color.green(), title=f'{ctx.guild.name} {T_emoji} Scores:')
          embed.set_footer(text=f'Requested by: {ctx.author.name}#{ctx.author.discriminator}')
          
          for pos, user_id in enumerate(current_keys, start=start_pos + 1):
              score_diff = leaderboard_data[user_id]
              user_member = ctx.guild.get_member(int(user_id))
              name_field = f'{pos}: {user_member.name}' if user_member else f'{pos}: Missing User'
              score_field = f'  {T_emoji} `{score_diff}`' if user_member else f'  {T_emoji} `{score_diff}` <@{user_id}>'
              embed.add_field(name=name_field, value=score_field, inline=False)
          
          return embed
      current_pos = 0
      message = await ctx.send(embed=create_leaderboard_embed(leaderboard_keys[:10], current_pos))

      def check_reaction(reaction, user):
          return str(reaction.emoji) in ["▶️", "◀️"] and user.id == ctx.author.id and reaction.message.id == message.id

      while True:
          try:
              await message.add_reaction("◀️")
              await message.add_reaction("▶️")
              reaction, user = await self.bot.wait_for('reaction_add', timeout=120.0, check=check_reaction)
          except Exception:
              break

          await message.remove_reaction(reaction.emoji, user)  # remove the reaction

          # Update the leaderboard position based on reaction
          if str(reaction.emoji) == "◀️":
              current_pos = max(current_pos - 10, 0)
          # Only allow moving forward if there are more users beyond the current view
          elif str(reaction.emoji) == "▶️" and current_pos + 10 < len(leaderboard_keys):
              current_pos = min(current_pos + 10, len(leaderboard_keys) - 10)

          # Create a new embed with the updated leaderboard view
          current_keys = leaderboard_keys[current_pos:current_pos + 10]
          await message.edit(embed=create_leaderboard_embed(current_keys, current_pos))

    

    @commands.group(help='Admin commands for the bot', aliases=['ea'])
    @commands.has_permissions(administrator=True)
    async def eAdmin(self, ctx):
      if ctx.invoked_subcommand is None:
        await ctx.send('Invalid admin command passed. Git gud')

    
    @eAdmin.command(help='Show which channels spawn, and the values for those channels!', aliases=['cl', 'chalist', 'channellist'])
    async def chaList(self, ctx):
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
    

    @eAdmin.command(help='Stop a channel from spawning. Admin only', aliases=['ChaDel', 'channelremove', 'channeldelete'])
    @commands.has_guild_permissions(administrator=True)
    async def chaRemove(self, ctx, cha:discord.TextChannel):
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


    @eAdmin.command(help='Start spawning in a channel. Admin only', aliases=['channeladd, chaadd'])
    @commands.has_guild_permissions(administrator=True)
    async def chaAdd(self, ctx, cha:discord.TextChannel, minScore=5, maxScore=10):
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


    @eAdmin.command(help='Update the spawnrate. Admin only', aliases=['ChaUp', 'channelupdate'])
    @commands.has_guild_permissions(administrator=True)
    async def chaUpdate(self, ctx, cha:discord.TextChannel, minScore=5, maxScore=10):
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
        
    
    @eAdmin.command(help='Send a backup of the database')
    @commands.check(is_it_me)
    async def backup(self, ctx):
      guildid = ctx.guild.id
      i = guildScores(guildid)
      embed = discord.Embed(color=Color.green(), title='Current user database for this guild:', description=str(i))
      await ctx.send(embed=embed)


    @eAdmin.command(help='Fix the event if they aren\'t working, Admin only', aliases=['fixme', 'workyoustupidbot'])
    @commands.has_guild_permissions(administrator=True)
    async def fix(self, ctx):
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
    

    @eAdmin.command(help='Reset the scores for this server.')
    @commands.check(is_it_me)
    async def reset(self, ctx):
      guildid = ctx.guild.id
      dev = self.bot.get_user(585991293377839114)
      i = guildScores(guildid)
      embed = discord.Embed(color=Color.green(), title='Current user database', description=str(i))
      await dev.send(embed=embed)
      removeGld(guildid)
      embed2 = discord.Embed(color=Color.green(), title='Database has been cleared. Its a new dawn!')
      await ctx.send(embed=embed2)
      await ctx.message.delete()


    @eAdmin.command(help='Check bot status, Dev only')
    @commands.check(is_it_me)
    async def check(self, ctx):
      embed = discord.Embed(color=Color.green(), title='Current variable status')
      embed.add_field(name='Current Emoji:', value=self.bot.get_emoji(emoji))
      embed.add_field(name='Waiting for a emoji to be claimed:', value=self.Twait)
      embed.add_field(name='Messages counted:', value=self.chatA)
      embed.add_field(name='Target messages before spawn:', value=self.chatTar)
      await ctx.send(embed=embed)
      

    
async def setup(bot):
  await bot.add_cog(Event(bot))


# old leaderboard code
# @commands.command(help='View the leaderboard', aliases=['lb'])
#     @commands.check(notGeneral)
#     async def leaderboard(self, ctx):
#       await ctx.channel.typing()
#       guildid = ctx.guild.id
#       lbid = guildScores(guildid)
#       #print(lbid)
#       lbid1 = list(lbid.keys())
#       if len(lbid1) > 9:
#         top10 = lbid1[:10]
#       else:
#         top10 = lbid1[:len(lbid1)]
#       #print(top10)
#       Temoji = self.bot.get_emoji(getEmote(ctx.guild.id))  
#       def CreateLb(current10, cPos): #current10 is the dict set of current id+score, cPos is the position of those ids
#         cembed = discord.Embed(color=Color.green(), title=f'{ctx.guild.name} {Temoji} Leaderboard:')
#         cembed.set_footer(text=f'Requested by: {ctx.author.name}#{ctx.author.discriminator}')
#         #print(current10)
#         for uid in current10:
#           #print(uid)
#           cPos+=1
#           uscore = lbid[uid]
#           umember = ctx.guild.get_member(int(uid))
#           #print(umember)
#           if not umember == None: 
#             names = f'{cPos}: {umember.name}'
#             uscore = f'  {Temoji} `{uscore}`'
#           else:
#             names = f'{cPos}: Missing User'
#             uscore = f'  {Temoji} `{uscore}` <@{uid}>'
#           cembed.add_field(name=names, value=uscore, inline=False)
#         return cembed
#       currentpos = 1
#       #send the first message
#       messagel = await ctx.send(embed=CreateLb(top10, 0))
#       #await ctx.message.delete()
#       def check(reaction, user):
#         return str(reaction.emoji) == "▶️" or str(reaction.emoji) == "◀️" and user.id == ctx.author.id and reaction.message.id == messagel.id
#       while True:
#         try:
#           await messagel.add_reaction("◀️")
#           await messagel.add_reaction("▶️")
#           reaction, user = await self.bot.wait_for('reaction_add', timeout=120.0, check=check)
#         except Exception:
#           break
#         if str(reaction.emoji) == "◀️" and user.id == ctx.author.id:
#           #move back
#           await messagel.remove_reaction("◀️",user)
#           #check if maxed out
#           if currentpos <= 1:
#             pass
#           else:
#             currentpos-=1 
#             #deal with short leaderboards
#             if len(lbid) > (currentpos*10):
#               current10 = lbid1[(currentpos*10-9):]
#             #deal with 10 leaderboards
#             if len(lbid) > (currentpos*10):
#               current10 = lbid1[(currentpos*10-10):(currentpos*10)]
#             await messagel.edit(embed=CreateLb(current10, ((currentpos*10)-10)))
#         if str(reaction.emoji) == "▶️" and user.id == ctx.author.id:
#           #move forward
#           await messagel.remove_reaction("▶️",user)
#           #check if maxed out
#           if len(lbid) <= (currentpos*10):
#             pass
#           else:
#             currentpos+=1 
#             #deal with short leaderboards
#             if len(lbid) > (currentpos*10):
#               current10 = lbid1[(currentpos*10-10):]
#             #deal with 10 leaderboards
#             if len(lbid) > (currentpos*10):
#               current10 = lbid1[(currentpos*10-10):(currentpos*10)]
#             await messagel.edit(embed=CreateLb(current10, ((currentpos*10)-10)))