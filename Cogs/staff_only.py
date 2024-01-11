import discord, os, sys, json, random, logging, requests
from discord.ext import commands
#from replit import db
from discord import Embed, Color, ui
#import sqlite3
import psycopg2 as pgsql
from init import conn, curr, is_it_me


# Custom check to see if the user is an admin member
def is_admin(ctx):
    # Adminrole is 470547452873932806, on break is 844400909927710780
    #print(ctx.author.roles)
    for role in ctx.author.roles:
      if role.id in [470547452873932806, 844400909927710780]:
        return True
    return False


def get_ar():
  l = {}
  curr.execute('SELECT * FROM reactions ORDER BY trigger')
  for row in curr:
    l[row[1]] = row[2]
  return l

def remove_ar(trigger):
  curr.execute('DELETE FROM reactions WHERE trigger = %s', (trigger,))
  conn.commit()

# Staff only commands
class StaffOnly(commands.Cog):
    def __init__(self, bot):
      self.bot = bot
      self.description = 'Staff only! Epic commands to improve your experiance!'

    #events
    @commands.Cog.listener()
    async def on_ready(self):
      print('staff_only is online')

    @commands.command(help='Send an embed, Admin only', aliases=['embed','emg'])
    @commands.check(is_admin)
    async def embed_msg(self, ctx, *, msg):
      await ctx.channel.typing()
      embed = Embed(color=Color.magenta(), title=msg)
      await ctx.send(embed=embed)
      cha = self.bot.get_channel(777042897630789633)
      await cha.send(str(ctx.author)+' used embed with msg: ' + str(msg))
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
    @commands.check(is_admin)
    async def ar_add(self, ctx, iemoji, trigger):      
      emoji=iemoji
      print(f'{emoji}:{trigger}')
      curr.execute('INSERT INTO reactions(trigger, eid) VALUES (%s, %s)', (str(trigger), str(emoji)))
      conn.commit()
      await ctx.send(f'{emoji} added for the trigger **{trigger}**')

    @commands.command(help='Check the list of autoreactions! Dev only')
    @commands.check(is_admin)
    async def ar_list(self, ctx):
        dab = get_ar()
        m = ""
        l = ""
        for i in dab:
          if len(i) > 15:
            m += f"(ID) - <@{i}> : {dab[i]}\n"
          else:
            m += f"{i} : {dab[i]}\n"
          if len(m) > 1700:
            l = m
            m = ''
        if l != '':
          await ctx.send(f'{l}', allowed_mentions=discord.AllowedMentions.none())
        await ctx.send(f'{m}')
          

    @commands.command(help="Delete an autoreaction. Dev only")
    @commands.check(is_admin)
    async def ar_del(self, ctx, trigger):
        remove_ar(trigger)
        await ctx.send(f'{trigger} has been removed.')

    @ar_del.error
    async def ar_del_error(self, ctx, error):
      await ctx.send(f'Error: {error}')

    @commands.command(help='Change my status! Dev only')
    @commands.has_role(827016494998093834) #470547452873932806 is admin role
    async def status_change(self, ctx, *, msgd):
      streaming=discord.Game(name=msgd)
      await self.bot.change_presence(status=discord.Status.dnd, activity=streaming)
      await ctx.reply('Done!')


    @commands.command(help='Change Staff Alert Level')
    @commands.has_any_role(470547452873932806, 670427731468746783, 714891905392967691)
    async def alert(self, ctx, alert):
      print(alert)
      await ctx.channel.typing()
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
    
    @commands.command(help="Manually verify a member", aliases=['mv', 'verify'])
    @commands.check(is_admin)
    async def manualverify(self, ctx, nusr:discord.Member):
      print("Manual verify triggered")
      role1 = ctx.guild.get_role(702710000048668783)
      await nusr.add_roles(role1)
      print("added role")
      channel = ctx.guild.get_channel(670362292659159040)
      await channel.send(f'Welcome, <@{nusr.id}> as the {ctx.guild.member_count}th user!')
      await nusr.send(content='You have been manually verified. Say hi in <#670362292659159040>!')
      await ctx.reply(f'Done. <@{nusr.id}> has been manually verified.')
    
    @manualverify.error
    async def mv_error(self, ctx, error):
      await ctx.send(f'Error: {error}', delete_after=15)

async def setup(bot):
  await bot.add_cog(StaffOnly(bot))
