import discord, os, sys, json, random, logging, requests
from discord.ext import commands
#from replit import db
from discord import Embed, Color, ui
import sqlite3

con = sqlite3.connect('/root/data/data1.db')
cur = con.cursor()


#db['StaffAlert'] = 3
#db['newreacts'] = {'wolfie': '<:wolfygun:755447204654874696>', 'wingy': '<:wingyafterashower:771542730916364338>', 'ereg': '<:ninjathonk:827739388058140713>', 'wolfy': '<:wolfyrpg:844992590361526272>', 'wofy': '<:wolfyrpg:844992590361526272>', 'marsh': '<:marshyhappy:826259233309196348>', 'dasani': '<:sunglase:834052568271159297>', 'delta': '<:whot:792770838113026058>', 'pog': '<:pog:706201125275303950>', 'andokrin': '<:Kannasip:762753253016338512>', 'jeff': '<:blink:767221910374318150>', 'abuse': '<:catstare:850751387889434624>', 'sensei': '<:thumbsup:851910615168974878>', 'morgy': '<:thumbsup:851910615168974878>', 'bear': '<a:SaucyBear:762798329250709534>', 'demon': '<:YOURFEET:853123667314999317>', 'sparkle': '<:SPARKELS:853036933684658176>', 'mercury': '<:Mercury:881922010123468831>'}

def is_it_me(ctx):
    return ctx.message.author.id == 585991293377839114



class StaffOnly(commands.Cog):
    def __init__(self, bot):
      self.bot = bot

    #events
    @commands.Cog.listener()
    async def on_ready(self):
      print('staff_only is online')

    @commands.command(help='Send an embed, Admin only', aliases=['embed','emg'])
    @commands.has_role(470547452873932806)
    async def embed_msg(self, ctx, *, msgd):
      await ctx.channel.trigger_typing()
      embed = Embed(color=Color.magenta(), title=msgd)
      await ctx.send(embed=embed)
      cha = self.bot.get_channel(777042897630789633)
      await cha.send(str(ctx.author)+' used embed with msg: ' + str(msgd))
      await ctx.message.delete()

    @commands.command(help='Get help with lag in-game')
    @commands.has_any_role(710340565652209765, 702710009850757140, 377174344197079043)
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def lag(self, ctx):
      msg = 'Improving lag within ninja.io:'
      mlist = ['Turn off anti-aliasing and shockwave effects in the settings. (they are disabled by default).', 
      'Decrease the window size. When you run ninja.io in a smaller window, it will run faster on systems with limited graphics capability. This can make a big difference.',
      'Don\'t run other games, programs, videos or websites in the background.',
      'Make sure that your graphics drivers are up to date.', 
      'Try a different browser.']
      embed = Embed(color=Color.green(), title=msg)
      l=0
      for item in mlist:
        l+=1
        embed.add_field(name=str(l)+': ', value=item, inline=False)
      await ctx.reply(embed=embed)


    @commands.command(help='Add an emojireaction, Dev only')
    @commands.check(is_it_me)
    async def ar_add(self, ctx, iemoji, trigger):      
      emoji=iemoji
      print(f'{emoji}:{trigger}')
      #dab = db['newreacts']
      #dab[str(trigger)] = str(emoji)
      #print(dab)
      #db['newreacts'] = dab
      cur.execute('INSERT INTO reactions(trigger, eid) VALUES (?, ?)', (str(trigger), str(emoji)))
      con.commit()
      await ctx.send(f'{emoji} added for the trigger **{trigger}**')

    '''@commands.command(help='Check the list of autoreactions! Dev only')
    @commands.check(is_it_me)
    async def ar_list(self, ctx):
        dab = db["newreacts"]
        m = ""

        for i in dab:
          m += f"{i} : {dab[i]}\n"
        
        await ctx.send(m)

    @commands.command(help="Delete an autoreaction. Dev only")
    @commands.check(is_it_me)
    async def ar_del(self, ctx, trigger):
        dab = db["newreacts"]
        if trigger in dab:
          del dab[trigger]
          db["newreacts"] = dab
          await ctx.send(f"{trigger} has been removed from database.")
        else:
          await ctx.send("Trigger not found.")


        @ar_add.error
        async def ar_add_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
          await ctx.send(f'Error: {error}')'''

    @commands.command(help='Change my status! Dev only')
    @commands.has_role(827016494998093834)
    async def status_change(self, ctx, *, msgd):
      streaming=discord.Game(name=msgd)
      await self.bot.change_presence(status=discord.Status.dnd, activity=streaming)
      await ctx.reply('Done!')


    @commands.command(help='Change Staff Alert Level')
    @commands.has_any_role(470547452873932806, 670427731468746783, 714891905392967691)
    async def alert(self, ctx, alert):
      print(alert)
      await ctx.channel.trigger_typing()
      try:
        alert = int(alert)
      except Exception:
        await ctx.send("Please enter a valid alert value")
        return
      if alert > 4 or alert < 0:
        await ctx.send("Please enter a valid alert value")
        return
      channelid = 871866974307762246
      channel1 = ctx.guild.get_channel(channelid)
      #print(channel1)
      #print(message1)
      if alert == 1:
        msgd = "Low Alert - 1"
        chad = "Tier 1 Low Alert"
      elif alert == 2:
        msgd = "Medium Alert - 2"
        chad = "❗Tier 2 Medium Alert❗"
      elif alert == 3:
        msgd = "High Alert - 3"
        chad = "❗❗Tier 3 High Alert❗❗"
      elif alert == 4:
        msgd = "Extreme Alert - 4"
        chad = "❗❗❗Tier 4 Extreme Alert❗❗❗"
      await channel1.purge(limit=1)
      embed = Embed(color=Color.magenta(), title=msgd)
      await channel1.send(embed = embed)
      await channel1.edit(name=chad, reason='Changed Alert Level')
      #if int(db["StaffAlert"]) < alert:
        #await channel1.send(f"@here Staff Alert Level has been raised to {str(alert)}!",  delete_after=30)
      #db["StaffAlert"] = alert
      await ctx.send(f"Done. Alert level is now {str(alert)}.")
    
    '''@commands.command(help="export the repl data")
    @commands.check(is_it_me)
    async def export(self, ctx):
      keys = db.keys()
      for key in keys:
        print(f"{key}:{db[key]}\n")
        await ctx.send(f"{key}:{db[key]}")'''
    

      

def setup(bot):
  bot.add_cog(StaffOnly(bot))
