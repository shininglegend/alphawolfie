import discord, os, sys, json, random, logging, requests
from discord.errors import Forbidden
from discord import message
from discord.ext.commands.core import has_any_role
from discord.ext import commands
#from replit import db
from discord import Embed, Color
import sqlite3

con = sqlite3.connect('/root/data/data1.db')
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS suggestions2 (id INTEGER PRIMARY KEY AUTOINCREMENT, msgid INTEGER, userid INTEGER, content TEXT, edited INTEGER DEFAULT 0, response TEXT DEFAULT 'None', responseid INTEGER DEFAULT 0)")
#cur.execute('ALTER TABLE suggestions2 ADD responseid INTEGER DEFAULT 0')
con.commit()
#add a suggestion to the database
def suggestion_add(userid, msgid, suggestion):
    cur.execute('INSERT INTO suggestions2(userid, msgid, content) VALUES (?, ?, ?)', (userid, msgid, suggestion))
    con.commit()    

def update_suggestion(id, field, value):
    cur.execute('UPDATE suggestions2 SET ? = ? WHERE id = ?',  (field, value, id))
    cur.commit()   

class Suggestion(commands.Cog):

    def __init__(self, bot):
      self.bot = bot

    #events
    @commands.Cog.listener()
    async def on_ready(self):
      print('Suggestion is online')
    
    async def suggestion_update(self, ctx, sid, reply, status):
      await ctx.message.delete()
      suggestionfetched = None
      try:
        print(sid)
        sid = int(sid)
        for row in cur.execute(f'SELECT * FROM suggestions2 WHERE id = {sid}'):
          suggestionfetched = row
      except Exception:
        await ctx.send("Please enter a valid suggestion value.", delete_after=5)
        return
      print(suggestionfetched)
      if suggestionfetched==None:
        await ctx.send("I could not find that suggestion.", delete_after=5)
        return
      sgsmsgid = suggestionfetched[1]
      sgscontent = suggestionfetched[3]
      usr = ctx.guild.get_member(suggestionfetched[2])
      cha = ctx.guild.get_channel(670362431373180948)
      msg3 = await cha.fetch_message(sgsmsgid)
      statusO = {"a":"approved", "d":"denied", "c":"considered"} #response options
      statusC = {"a":Color.green(), "d":Color.red(), "c":Color.yellow()} #Color options
      reply2 = status + reply
      #update_suggestion(sid, "response", reply2)
      #update_suggestion(sid, "responseid", ctx.author.id)
      print(msg3)      
      embed4= Embed(color=statusC[status], title=f"Suggestion #{sid}", description=sgscontent)
      embed4.set_author(name=f'{usr.name}#{usr.discriminator}', icon_url=usr.display_avatar)
      embed4.add_field(name=f'{statusO[status].capitalize()} by {ctx.author.name}#{ctx.author.discriminator}', value=reply)
      await msg3.edit(embed=embed4)
      embed4.add_field(name="See the message here:", value=msg3.jump_url, inline=False)
      try:
        await usr.send(content=f"Hey there!\nYour suggestion has been __{statusO[status]}__ by **{ctx.author.name}#{ctx.author.discriminator}**:", embed=embed4)
      except Forbidden:
        print(f'I couldn\'t DM {usr.name}#{usr.discriminator}')

    #commands

    #suggestion command
    @commands.command(help='Make a suggestion related to the game or discord!')
    @commands.cooldown(1, 20)
    async def suggest(self, ctx, *, suggestion):
        #add it to the database and return id
        for row in cur.execute('SELECT MAX(id) FROM suggestions2'):
            suggestionid = row[0]
            suggestionid = 2222
        suggestionid = int(suggestionid) + 1
        #post the suggestion
        embed2 = discord.Embed(color=Color.dark_magenta(), title=f"Suggestion #{suggestionid}", description=suggestion)
        embed2.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.display_avatar)
        cha = ctx.guild.get_channel(670362431373180948)
        msg2 = await cha.send(embed=embed2)
        await msg2.add_reaction("<:upvote:904548817783894026>")
        await msg2.add_reaction("<:downvote:904548736884150292>")
        suggestion_add(ctx.author.id, msg2.id, suggestion)
        await ctx.reply("Suggestion added in <#670362431373180948>.", delete_after=10)
        await ctx.message.delete()
        print(f'Added suggestion from {ctx.author.name}#{ctx.author.discriminator}')
    #approve command
    @commands.command(help='Approve a suggestion')
    @commands.check(has_any_role(470547452873932806, 670427731468746783, 7103405656522097650))
    async def approve(self, ctx, sid, *, reply="No reason given"):
      await self.suggestion_update(ctx=ctx, sid=sid, reply=reply, status='a')
      
    #deny command
    @commands.command(help='Deny a suggestion')
    @commands.check(has_any_role(470547452873932806, 670427731468746783, 7103405656522097650))
    async def deny(self, ctx, sid, *, reply="No reason given"):
      await self.suggestion_update(ctx=ctx, sid=sid, reply=reply, status='d')

    #consider command
    @commands.command(help='Consider a suggestion')
    @commands.check(has_any_role(470547452873932806, 670427731468746783, 7103405656522097650))
    async def consider(self, ctx, sid, *, reply="No reason given"):
      await self.suggestion_update(ctx=ctx, sid=sid, reply=reply, status='c')
      
    #edit command
    @commands.command(help='Edit your a suggestion, or a suggestion by someone else if staff', disabled=True)
    async def edit(self, ctx, sid1, *, reply):
      rolelist = []
      rolelist1 = []
      for roleid in rolelist:
        rolelist1.append(await ctx.guild.get_role(roleid))
      try:
        print(sid1)
        sid1 = int(sid1)
        for row in cur.execute(f'SELECT * FROM suggestions2 WHERE id = {sid1}'):
          suggestionfetched = row
      except Exception:
        await ctx.send("Please enter a valid suggestion value", delete_after=5)
        return
      print(suggestionfetched)
      sgsmsgid = suggestionfetched[1]
      sgscontent = suggestionfetched[3]
      usr = ctx.guild.get_member(suggestionfetched[2])
      cha = ctx.guild.get_channel(670362431373180948)
      msg4 = await cha.fetch_message(sgsmsgid)
      #rspstatus = getresponsestatus()




def setup(bot):
  bot.add_cog(Suggestion(bot))
