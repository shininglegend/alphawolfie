import discord, os, sys, json, random, logging, requests
from discord.ext.commands.core import has_any_role
from discord.ext import commands
#from replit import db
from discord import Embed, Color
import sqlite3

con = sqlite3.connect('/rool/data/data1.db')
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS suggestions2 (id INTEGER PRIMARY KEY AUTOINCREMENT, msgid INTEGER, userid INTEGER, content TEXT, edited INTEGER DEFAULT 0, response TEXT DEFAULT 'None')")
#add a suggestion to the database
def suggestion_add(userid, msgid, suggestion):
    cur.execute('INSERT INTO suggestions2(userid, msgid, content) VALUES (?, ?, ?)', (userid, msgid, suggestion))
    con.commit()    
    
    

class Suggestion(commands.Cog):

    def __init__(self, bot):
      self.bot = bot

    #events
    @commands.Cog.listener()
    async def on_ready(self):
      print('Suggestion is online')

    #commands

    #suggestion command
    @commands.command(help='Make a suggestion related to the game or discord!')
    @commands.cooldown(1, 20)
    async def suggest(self, ctx, *, suggestion):
        #add it to the database and return id
        #suggestion_add(809948529941413929, 904948087154438185, "CTF rankings")
        for row in cur.execute('SELECT MAX(id) FROM suggestions2'):
            suggestionid = row[0]
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
    async def approve(self, ctx, sid, *, reply):
      await ctx.message.delete()
      try:
        print(sid)
        sid = int(sid)
        for row in cur.execute(f'SELECT * FROM suggestions2 WHERE id = {sid}'):
            suggestionfetched = row
      except Exception:
        await ctx.send("Please enter a valid suggestion value", delete_after=5)
        return
      print(suggestionfetched)
      sgsmsgid = suggestionfetched[1]
      sgscontent = suggestionfetched[3]
      usr = ctx.guild.get_member(suggestionfetched[2])
      cha = ctx.guild.get_channel(670362431373180948)
      msg3 = await cha.fetch_message(sgsmsgid)
      print(msg3)
      embed4= Embed(color=Color.green(), title=f"Suggestion #{sid}", description=sgscontent)
      embed4.set_author(name=f'{usr.name}#{usr.discriminator}', icon_url=usr.display_avatar)
      embed4.add_field(name=f'Approved by {ctx.author.name}#{ctx.author.discriminator}', value=reply)
      await msg3.edit(embed=embed4)
        
    #deny command
    @commands.command(help='Deny a suggestion')
    @commands.check(has_any_role(470547452873932806, 670427731468746783, 7103405656522097650))
    async def deny(self, ctx, sid, *, reply):
      await ctx.message.delete()
      try:
        print(sid)
        sid = int(sid)
        for row in cur.execute(f'SELECT * FROM suggestions2 WHERE id = {sid}'):
            suggestionfetched = row
      except Exception:
        await ctx.send("Please enter a valid suggestion value", delete_after=5)
        return
      print(suggestionfetched)
      sgsmsgid = suggestionfetched[1]
      sgscontent = suggestionfetched[3]
      usr = ctx.guild.get_member(suggestionfetched[2])
      cha = ctx.guild.get_channel(670362431373180948)
      msg3 = await cha.fetch_message(sgsmsgid)
      print(msg3)
      embed4= Embed(color=Color.red(), title=f"Suggestion #{sid}", description=sgscontent)
      embed4.set_author(name=f'{usr.name}#{usr.discriminator}', icon_url=usr.display_avatar)
      embed4.add_field(name=f'Denied by {ctx.author.name}#{ctx.author.discriminator}', value=reply)
      await msg3.edit(embed=embed4)
    #edit command?

    #consider command
    @commands.command(help='Consider a suggestion')
    @commands.check(has_any_role(470547452873932806, 670427731468746783, 7103405656522097650))
    async def consider(self, ctx, sid, *, reply):
      await ctx.message.delete()
      try:
        print(sid)
        sid = int(sid)
        for row in cur.execute(f'SELECT * FROM suggestions2 WHERE id = {sid}'):
          suggestionfetched = row
      except Exception:
        await ctx.send("Please enter a valid suggestion value", delete_after=5)
        return
      print(suggestionfetched)
      sgsmsgid = suggestionfetched[1]
      sgscontent = suggestionfetched[3]
      usr = ctx.guild.get_member(suggestionfetched[2])
      cha = ctx.guild.get_channel(670362431373180948)
      msg3 = await cha.fetch_message(sgsmsgid)
      print(msg3)
      embed4= Embed(color=Color.yellow(), title=f"Suggestion #{sid}", description=sgscontent)
      embed4.set_author(name=f'{usr.name}#{usr.discriminator}', icon_url=usr.display_avatar)
      embed4.add_field(name=f'Considered by {ctx.author.name}#{ctx.author.discriminator}', value=reply)
      await msg3.edit(embed=embed4)
    #comment command?


def setup(bot):
  bot.add_cog(Suggestion(bot))
