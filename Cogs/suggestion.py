import discord, os, sys, json, random, logging, datetime
from discord.errors import Forbidden
from discord import message
from discord.ext.commands.core import has_any_role
from discord.ext import commands
#from replit import db
from discord import Embed, Color, app_commands
# import sqlite3
import psycopg2 as pgsql

conn = pgsql.connect("dbname=alphawolfie user=postgres password=password")
#con = sqlite3.connect('data1.db')
curr = conn.cursor()
#con = sqlite3.connect('/root/data/data1.db')

#cur = con.cursor()
#curr.execute("CREATE TABLE IF NOT EXISTS suggestions2 (id INTEGER PRIMARY KEY AUTOINCREMENT, msgid INTEGER, userid INTEGER, content TEXT, edited INTEGER DEFAULT 0, response TEXT DEFAULT 'None', responseid INTEGER DEFAULT 0, thread BIGINT DEFAULT 0)")
#conn.commit()

# add a suggestion to the database
def suggestion_add(vid, userid, msgid, suggestion, thread):
    curr.execute('INSERT INTO suggestions2(visual_id, userid, msgid, content, thread) VALUES (%s, %s, %s, %s, %s)', (vid, userid, msgid, suggestion, thread))
    conn.commit()    

def update_suggestion(id, usr, value):
    curr.execute('UPDATE suggestions2 SET (response, responseid) = (%s, %s) WHERE visual_id = %s',  (value, usr, id))
    conn.commit()   
def edit_suggestion(id, uid, value):
    curr.execute('UPDATE suggestions2 SET (content, edited) = (%s, %s) WHERE visual_id = %s',  (value, uid, id))
    conn.commit()

class Suggestion(commands.Cog):
    def __init__(self, bot):
      self.bot = bot
      self.description = 'Want something? Let us know using these commands.'

    async def log0101(self, message, title=None):
      print('logging event')
      cha = await self.bot.fetch_channel(777042897630789633)
      if not title:
        title="Logged Event:"
      embed3 = Embed(title=title, description=message, color=Color.green(), timestamp=datetime.datetime.now())
      await cha.send(embed=embed3)

    # events
    @commands.Cog.listener()
    async def on_ready(self):
      print('Suggestion is online')      

    async def suggestion_update(self, ctx, sid, reply, status):
      await ctx.message.delete()
      try:
        #print(sid)
        sid = int(sid)
        curr.execute('SELECT * FROM suggestions2 WHERE visual_id = %s', (sid,))
        suggestionfetched = curr.fetchone()
        if suggestionfetched == None:
          raise Exception('404. Not found in database.')
      except Exception:
        await ctx.send("Please enter a valid suggestion value", delete_after=5)
        return
      # id, msgid, userid, content, edited, response, responseid, thread = 8
      #for index, i in enumerate(suggestionfetched):
        #print(i, index)
      sgsmsgid = suggestionfetched[1]
      sgscontent = suggestionfetched[3]
      sgseditusr = ctx.guild.get_member(suggestionfetched[4])
      usr = ctx.guild.get_member(suggestionfetched[2])
      thread = await self.bot.fetch_channel(suggestionfetched[8])
      if usr == None:
        await ctx.send("User not found in server.", delete_after=5)
        print("Failed to find user. Cannot edit suggestion.")
        return
      cha = ctx.guild.get_channel(670362431373180948)
      msg3 = await cha.fetch_message(sgsmsgid)
      statusO = {"a":"approved", "d":"denied", "c":"considered"} # response options
      statusC = {"a":Color.green(), "d":Color.red(), "c":Color.yellow()} # Color options
      reply2 = status + reply
      update_suggestion(sid, usr.id, reply2)
      #update_suggestion(sid, "response", reply2)
      #update_suggestion(sid, "responseid", ctx.author.id)
      #print(msg3)      
      embed4= Embed(color=statusC[status], title=f"Suggestion #{sid}", description=sgscontent)
      embed4.set_author(name=f'{usr.name}#{usr.discriminator}', icon_url=usr.display_avatar)
      embed4.add_field(name=f'{statusO[status].capitalize()} by {ctx.author.name}#{ctx.author.discriminator}', value=reply)
      if sgseditusr != None:
        embed4.set_footer(text=f'---------------------\nEdited by {sgseditusr.name}#{sgseditusr.discriminator}')
      await msg3.edit(embed=embed4)
      # If this was a denial, clear reactions
      if status == "d":
        await msg3.clear_reactions()
      embed4.add_field(name="See the message here:", value=msg3.jump_url, inline=False)
      try:
        await usr.send(content=f"Hey there!\nYour suggestion has been __{statusO[status]}__ by **{ctx.author.name}#{ctx.author.discriminator}**:", embed=embed4)
      except Forbidden:
        print(f"I couldn't DM {usr.name}#{usr.discriminator}")
        await self.log0101(f'I couldn\'t DM {usr.name}#{usr.discriminator}')
      # Close the thread if this wasn't just an consider status
      print(thread)
      if status == "a" and thread != None:
        # Lock the thread and send a message to confirm
        await thread.edit(locked=True, name=f"Closed: {thread.name}")
        await thread.send(f'This thread has been closed as the suggestion has been marked as {statusO[status]}.')
      # If this was a denial, delete the thread
      if status == "d" and thread != None:
        await thread.delete()
        await self.log0101(f'Deleted thread "{thread.name}" as the suggestion was denied.')
      # Send a message to confirm
      await ctx.send(f'Suggestion #{sid} has now been marked as {statusO[status]} with reason:\n`{reply}`', delete_after=5)

    # commands

    # suggestion command
    @commands.command(help='Make a suggestion related to the game or discord!')
    @commands.cooldown(1, 20)
    async def suggest(self, ctx, *, suggestion):
        for i in ctx.author.roles:
          if i.id == 931394725511049256:
            await ctx.reply("❌ No ❌", delete_after=5)
            return
        # check if suggestion is too long
        if len(suggestion) > 1000:
            await ctx.send("Your suggestion is too long. Please keep it under 1000 characters.", delete_after=5)
            return
        # start typing
        await ctx.channel.typing()
        # add it to the database and return id
        #suggestion_add(809948529941413929, 904948087154438185, "CTF rankings")
        curr.execute('SELECT MAX(visual_id) FROM suggestions2')
        for row in curr:
            suggestionid = row[0]
        suggestionid = int(suggestionid) + 1
        # post the suggestion
        embed2 = discord.Embed(color=Color.dark_magenta(), title=f"Suggestion #{suggestionid}", description=suggestion)
        embed2.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.display_avatar)
        cha = ctx.guild.get_channel(670362431373180948)
        msg2 = await cha.send(embed=embed2)
        # Add a thread for discussion
        thread = await msg2.create_thread(name=f"#{suggestionid} - {suggestion[:min(20, len(suggestion))]}...", 
                                          auto_archive_duration=60, 
                                          slowmode_delay=10)
        # add it to the database
        suggestion_add(suggestionid, ctx.author.id, msg2.id, suggestion, thread.id)
        # add reactions based on if we have custom emojis or not
        try:
          await msg2.add_reaction("<:upvote:904548817783894026>")
          await msg2.add_reaction("<:downvote:904548736884150292>")
        except discord.errors.HTTPException:
          await msg2.add_reaction("👍")
          await msg2.add_reaction("👎")
        
        await ctx.reply("Suggestion added in <#670362431373180948>.", delete_after=10)
        await ctx.message.delete()
        print(f'Added suggestion from {ctx.author.name}#{ctx.author.discriminator}')

    # approve command
    @commands.command(help='Approve a suggestion')
    @commands.check(has_any_role(470547452873932806, 670427731468746783, 468181046048063490))
    async def approve(self, ctx, sid, *, reply="No reason given"):
      await self.suggestion_update(ctx=ctx, sid=sid, reply=reply, status='a')

    # deny command
    @commands.command(help='Deny a suggestion')
    @commands.check(has_any_role(470547452873932806, 670427731468746783, 468181046048063490))
    async def deny(self, ctx, sid, *, reply="No reason given"):
      await self.suggestion_update(ctx=ctx, sid=sid, reply=reply, status='d')
      

    # consider command
    @commands.command(help='Consider a suggestion')
    @commands.check(has_any_role(470547452873932806, 670427731468746783, 468181046048063490))
    async def consider(self, ctx, sid, *, reply="No reason given"):
      await self.suggestion_update(ctx=ctx, sid=sid, reply=reply, status='c')
      
    # edit command
    @commands.command(help='Edit your a suggestion, or a suggestion by someone else if staff')
    @commands.cooldown(1, 20)
    #@commands.check(has_any_role(470547452873932806, 670427731468746783, 7103405656522097650))
    async def edit(self, ctx, sid1, *, reply):
      for i in ctx.author.roles:
          if i.id == 931394725511049256:
            await ctx.reply("❌ No ❌", delete_after=5)
            return
      try:
        print(sid1)
        sid1 = int(sid1)
        curr.execute('SELECT * FROM suggestions2 WHERE visual_id = %s', (sid1,))
        suggestionfetched = curr.fetchone()
        if sid1 < 2302:
          raise Exception('That suggestion cannont be edited.')
      except Exception:
        await ctx.send("Please enter a valid suggestion value. \n*Keep in mind that suggestions with an id smaller than 2302 cannot be edited.*", delete_after=5)
        return
      print(suggestionfetched)
      # extract data from the database row
      cha = ctx.guild.get_channel(670362431373180948)
      sgsmsgid = suggestionfetched[1]
      msg4 = await cha.fetch_message(sgsmsgid)
      sgscontent = suggestionfetched[3]      
      usr = ctx.guild.get_member(suggestionfetched[2])
      thread = await self.bot.fetch_channel(suggestionfetched[8])
      # check if they are allowed to run the command or if they made the suggestion
      check=False
      for i in [470547452873932806, 670427731468746783, 7103405656522097650]:
          role = ctx.guild.get_role(i)
          if role in ctx.author.roles:
            check = True
      if not (check==True or usr.id==ctx.author.id):
        await ctx.send("You can only edit your own suggestions.", delete_after=5)
        return
      edit_suggestion(sid1, ctx.author.id, reply)
      sgsrespusr = suggestionfetched[6]
      sgsrespmsg = suggestionfetched[5]
      statusO = {"a":"approved", "d":"denied", "c":"considered"} # response options
      statusC = {"a":Color.green(), "d":Color.red(), "c":Color.yellow(), "n":Color.dark_magenta()} # Color options
      # check if its been replied to already
      if sgsrespusr in (0, 'None'):
        status = "n"
      else:
        status = sgsrespmsg[0]
        sgsrespmsg = sgsrespmsg[1:]
      # make the embed
      embed5= Embed(color=statusC[status], title=f"Suggestion #{sid1}", description=reply)
      embed5.set_footer(text=f'---------------------\nEdited by {ctx.author.name}#{ctx.author.discriminator}')
      embed5.set_author(name=f'{usr.name}#{usr.discriminator}', icon_url=usr.display_avatar)
      if sgsrespusr not in (0, 'None'):
        embed5.add_field(name=f'{statusO[status].capitalize()} by {ctx.author.name}#{ctx.author.discriminator}', value=sgsrespmsg)
      await msg4.edit(embed=embed5)
      await self.log0101(f'`Old message:` {sgscontent}\n`New message:` {reply}', f'Suggestion #{sid1} edited by {ctx.author.name}#{ctx.author.discriminator}:')
      # send a message to the thread if it exists
      if thread:
        await thread.send(f'Suggestion #{sid1} edited by {ctx.author.name}#{ctx.author.discriminator}:')
        await thread.send(f'`Old message:` {sgscontent}\n`New message:` {reply}')
      await ctx.reply('The suggestion has been edited.', delete_after = 5)
      await ctx.message.delete()

    #@edit.error
    #async def edit_error(self, ctx, error):
      #await ctx.send(f'Error: {error}', delete_after=15)

async def setup(bot):
  await bot.add_cog(Suggestion(bot))