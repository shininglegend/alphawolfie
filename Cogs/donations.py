
from ast import alias
import discord, requests, sys, json, random, logging, os, time, datetime
from discord.errors import Forbidden
from discord.ext import commands
#from replit import db
from discord import Embed, Color
#import sqlite3
import psycopg2 as pgsql

conn = pgsql.connect("dbname=alphawolfie user=postgres password=password")
#con = sqlite3.connect('/root/data/data1.db')
#con = sqlite3.connect('data1.db')

#cur = con.cursor()
curr = conn.cursor()
#print('I updated')

curr.execute('CREATE TABLE IF NOT EXISTS donations2 (id SERIAL PRIMARY KEY, userid BIGINT NOT NULL, amount BIGINT DEFAULT 0, monthly INTEGER DEFAULT 0)')
curr.execute('CREATE TABLE IF NOT EXISTS cache_accounts2 (id SERIAL PRIMARY KEY, amount BIGINT)')
curr.execute('SELECT * FROM cache_accounts2')
if curr.fetchone() == None:
    print('Setting new cache values')
    for i in range(0, 5):
        curr.execute('INSERT INTO cache_accounts2(id, amount) VALUES (%s, 0)', (i+1,))
        conn.commit() 

def checkGoldTotal(cachenumber):
    a = f'CacheNinja{cachenumber}'
    b = f'AliBabaPotato{cachenumber}098'      #pass in your username as 'a' and password and your password as 'b'
    c = requests.post('https://api.ninja.io/user/login', data= {'name': a, 'password': b})  #login
    if 'id' in c.json():                                                                    #check if your credentials are valid/nothing has gone horrible wrong
        time.sleep(0.1)                                                                     #per Buizerd request we have to limit api requests to 10 per second
        d = requests.get('https://api.ninja.io/user/currency/'+c.json()['id'])              #get the currency
        return int(d.json()['currency']['gold'])                                            #return an integer
    else:
        return 'Invalid'                                                                    #what it returns if something is wrong/invalid

def in_tickets():
    async def predicate(ctx):
        return ctx.channel.category_id == 960751047826108416
    return commands.check(predicate)

def get_amount(cachenumber):
    curr.execute('SELECT * FROM cache_accounts2 WHERE id = %s', (int(cachenumber),))
    account = curr.fetchone()
    print(account)
    return account[1]
def get_total(userid):
    curr.execute('SELECT * FROM donations2 WHERE userid = %s', (userid,))
    account = curr.fetchone()
    print(account)
    if account == None:
        return 0
    else: 
        return account[2]
def get_monthly(userid):
    curr.execute('SELECT * FROM donations2 WHERE userid = %s', (userid,))
    account = curr.fetchone()
    print(account)
    if account == []:
        return 0
    else: 
        return account[3]

def setcache(cachenumber, amount):
    curr.execute('UPDATE cache_accounts2 SET amount = %s WHERE id = %s',  (amount, cachenumber))
    conn.commit()

def setmember(userid, amount):
    curr.execute('SELECT * FROM donations2 WHERE userid = %s', (userid,))
    account = curr.fetchone()
    if account == None:
        ntotal = amount
        nmonthly = amount
        curr.execute('INSERT INTO donations2 (userid, amount, monthly) VALUES (%s, %s, %s)',  (userid, ntotal, nmonthly,))
    else:
        monthly = account[3]
        total = account[2]
        nmonthly = monthly + amount
        ntotal = total + amount
        curr.execute('UPDATE donations2 SET (amount, monthly) = (%s, %s) WHERE userid = %s',  (ntotal, nmonthly, userid))
    conn.commit()
    return nmonthly

def setmember2(userid, amount, monthly):
    curr.execute('SELECT * FROM donations2 WHERE userid = %s', (userid,))
    account = curr.fetchone()
    print(account)
    if account == None:
        curr.execute('INSERT INTO donations2 (userid, amount, monthly) VALUES (%s, %s, %s)',  (userid, amount, monthly,))
    else:
        curr.execute('UPDATE donations2 SET (amount, monthly) = (%s, %s) WHERE userid = %s',  (amount, monthly, userid,))
    conn.commit()

def guildScoresM():
  gscores = {}
  curr.execute('SELECT * FROM donations2 ORDER BY monthly DESC')
  for row in curr:
    #print(row)
    gscores[row[1]] = row[3]
  #print(gscores)
  return gscores 

def guildScoresT():
  gscores = {}
  curr.execute('SELECT * FROM donations2 ORDER BY amount DESC')
  for row in curr:
    #print(row)
    gscores[row[1]] = row[2]
  #print(gscores)
  return gscores 

class Donations(commands.Cog):

    def __init__(self, bot):
      self.bot = bot
      self.description = 'These commmands are for handling gold donations.'

    async def log0101(self, message, title=None):
      print('logging event')
      cha = await self.bot.fetch_channel(777042897630789633)
      if not title:
        title="Logged Event:"
      embed3 = Embed(title=title, description=message, color=Color.green(), timestamp=datetime.datetime.now())
      await cha.send(embed=embed3)

    #events
    @commands.Cog.listener()
    async def on_ready(self):
      print('Donations is online')
      curr.execute('SELECT * FROM cache_accounts2')
      m1 = curr.fetchall()
      print(m1)

    #check someones donations
    @commands.command(help='Check current donations from a member.')
    async def dcheck(self, ctx, member:discord.Member=None):
        if not member:
            member = ctx.author
        amount = get_monthly(member.id)
        total = get_total(member.id)
        msg = f'__{member.display_name}__ has donated {amount} this month!'
        embed = Embed(color=Color.green(), title=msg, description=f'__{member.display_name}__ total donations are {total}')
        await ctx.reply(embed=embed)

    @commands.command(help='Check current saved cache amounts.', aliases=['d_cache'])
    @commands.has_any_role(702011263680643173, 935919659872567366)
    async def dcache(self, ctx):
        embed = Embed(color=Color.green(), title='Current Cache Amounts:')
        t = 0
        for i in range(5):
            cacheamount = get_amount(i+1)
            t+=cacheamount
            embed.add_field(name=f'CacheNinja{i+1}', value=str(cacheamount))
        embed.description = 'Total collected = ' + str(t)
        await ctx.reply(embed=embed)

    #add donations, max 5000
    @commands.command(help='Take a donation')
    @commands.has_any_role(702011263680643173, 935919659872567366)
    async def d_add(self, ctx, member:discord.Member=None, amount=-1):
        #check for a valid donation amount
        try:
            amount = int(amount)
            if amount < 0 : 
                raise Exception('AmountNotValid')
            i=str(amount)
            if i[(len(i)-3):] != '000': 
              print(i[(len(i)-3):])
              raise Exception('AmountNotValid')
        except Exception:
            await ctx.send('This is not a valid donation amount! Donations must be a multiple of 1000.')
            return
        if not member:
            await ctx.send('Please provide a valid member.')
            return
        
        #split up between cache accounts and check:
        embed = discord.Embed(color=Color.yellow(), title = 'Please check the accounts to ensure they have the correct amount', description='Press the green checkmark when done.')

        #amount = 16000
        a=int(amount/1000)
        cachelist = {}
        o=0
        for i in range(5):
            if a > 5: o = round(a/5) #a=16 o=3
            if (o*5) > a: o-=1 #o=3, a=16, target added number for 1=4k, for 2,3,4,5=3k
            #a-(5*o)=1 16-(5*3)=1
            n = a-(5*o)
            if i+1 <= n: cacheamount = get_amount(i+1) + (o*1000) + 1000
            else: cacheamount = get_amount(i+1) + (o*1000)
            cachelist[i+1] = cacheamount
            embed.add_field(name=f'CacheNinja{i+1}', value=str(cacheamount))
        msg = await ctx.send(embed=embed)
        print(cachelist)
        
        def check(reaction, user):
            return str(reaction.emoji) == "✅" and user.id == ctx.author.id and reaction.message.id == msg.id
        while True:
            try:
                await msg.add_reaction("✅")
                reaction, user = await self.bot.wait_for('reaction_add', timeout=2000.0, check=check)
            except Exception:
                break
            if str(reaction.emoji) == "✅" and user.id == ctx.author.id:
                for i in cachelist:
                    cacheamount = cachelist[i]
                    print(cacheamount)
                    setcache(i, cacheamount)
                embed2 = discord.Embed(color=Color.green(), title = 'Confirmed. Below are the updated totals.')
                for i in cachelist:
                    cacheamount = cachelist[i]
                    embed2.add_field(name=f'CacheNinja{i}', value=str(cacheamount))
                await msg.edit(embed = embed2)
                memberamount = setmember(member.id, amount)
                await ctx.send(f'<@{member.id}>\'s new monthly total is {memberamount}. You may now close the ticket.')



    #edit a users donations or cache amounts
    @commands.command(help='Edit a users donations.')
    @commands.has_any_role(702011263680643173, 935919659872567366)
    async def d_change(self, ctx, monthly, total, member:discord.Member):
        try:
            amount = int(monthly)
            total = int(total)
            print('1')
            if any([amount < 0, total < 0]): 
                print('3')
                raise Exception('AmountNotValid')           
        except Exception:
            await ctx.send('This is not a valid donation amount! Donations must be a multiple of 1000.')
            return
        setmember2(member.id, total, monthly)
        await ctx.reply("I've updated that member\'s donations.")


    @commands.command(help='Edit a cache amount.', aliases=['setcache'])
    @commands.has_any_role(702011263680643173, 935919659872567366)
    async def set_cache(self, ctx, cache_number, amount):
        amount = int(amount)
        cnum = int(cache_number)
        setcache(cnum, amount)
        await ctx.send(f'CacheNinja{cnum} successfully set to {amount}.')

    #post monthly leaderboard.
    @commands.command(help='View the leaderboard, args are <month> or <total>', aliases=['dlb','donationslb'])
    async def d_lb(self, ctx, type='month'):
      if type not in ('month', 'total'):
          await ctx.send('That\'s not a valid type.')
          return
      await ctx.channel.typing()
      if type == 'month': type = 'Monthly'
      elif type == 'total': type = 'Total'
      if type == 'Monthly': lbid = guildScoresM()
      elif type == 'Total': lbid = guildScoresT()
      #print(lbid)
      lbid1 = list(lbid.keys())
      if len(lbid1) > 10:
        top10 = lbid1[:10]
      else:
        top10 = lbid1
      Temoji = '<:ninjaIO_gold:784151877594906665>'
      #print(top10)
      def CreateLb(current10, cPos): #current10 is the dict set of current id+score, cPos is the position of those ids
        cembed = discord.Embed(color=Color.green(), title=f'{type} Gold Donations Leaderboard:', description='Use `;d_lb total` for total donations!')
        cembed.set_footer(text=f'Requested by: {ctx.author.name}#{ctx.author.discriminator}.')
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
            if len(lbid) < (currentpos*10):
              current10 = lbid1[(currentpos*10-10):]
            #deal with 10 leaderboards
            elif len(lbid) > (currentpos*10):
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
            if len(lbid) < (currentpos*10):
              current10 = lbid1[(currentpos*10-10):]
            #deal with 10 leaderboards
            elif len(lbid) > (currentpos*10):
              current10 = lbid1[(currentpos*10-10):(currentpos*10)]
            await messagel.edit(embed=CreateLb(current10, ((currentpos*10)-10)))
        
    @commands.command(help='Reset the leaderboard per month.')
    @commands.has_any_role(702011263680643173, 935919659872567366)
    async def dreset (self, ctx):
      msg = await ctx.send('Please confirm that you want to reset. \n**THIS CANNOT BE UNDONE!**')
      await msg.add_reaction("✅")
      def check(reaction, user):
            return str(reaction.emoji) == "✅" and user.id == ctx.author.id and reaction.message.id == msg.id
      while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=120.0, check=check)
            except Exception:
                await msg.edit(content='This action has been canceled.')
            if str(reaction.emoji) == "✅" and user.id == ctx.author.id:
             #output the current database in some format
              me = self.bot.get_user(585991293377839114)
              curr.execute('SELECT * FROM donations2')
              db = curr.fetchall()
              await me.send(str(db))
            #reset the monthly totals only
              curr.execute('UPDATE donations2 SET monthly = %s'%(0,))
              conn.commit()
              curr.execute('SELECT * FROM donations2')
              db = curr.fetchall()
              await me.send(str(db))
              await ctx.send('The monthly donations have been reset.')

    #automatic donations, handles a multiple of 5000, need to add check for category
    @commands.command(help='Donate gold!')
    @in_tickets()
    async def donate(self, ctx, amount, member:discord.Member=None):
        msg = await ctx.send("Please wait while I process the donation.....")
        if not member: member = ctx.author
        #check for a valid donation amount
        try:
            amount = int(amount)
            if amount < 0 : 
                raise Exception('AmountNotValid')
            i=str(amount)
            if i[(len(i)-3):] != '000': 
              print(i[(len(i)-3):])
              raise Exception('AmountNotValid')
        except Exception:
            await msg.edit(content='This is not a valid donation amount! Donations must be a multiple of 1000 and no more than 5000 at a time.')
            return
        
        #split up between cache accounts and get stored values, compared to new values
        a=int(amount/1000)
        cachelist = {}
        o=0
        for i in range(5):
            if a > 5: o = round(a/5) #a=16 o=3
            if (o*5) > a: o-=1 #o=3, a=16, target added number for 1=4k, for 2,3,4,5=3k
            #a-(5*o)=1 16-(5*3)=1
            n = a-(5*o)
            if i+1 <= n: cacheamount = get_amount(i+1) + (o*1000) + 1000
            else: cacheamount = get_amount(i+1) + (o*1000)
            cachelist[i+1] = cacheamount
        print(cachelist)
        #check if stored values match up to what was said to be donated
        e = 0
        for cachenum in cachelist:
          if checkGoldTotal(cachenum) >= cachelist[cachenum]:
            e += 1
        #if they do, process the donation.
        if e == len(cachelist):
          for i in cachelist:
            cacheamount = checkGoldTotal(i)
            print(cacheamount)
            setcache(i, cacheamount)
          embed2 = discord.Embed(color=Color.green(), title = 'Successfully processed.')
          for i in cachelist:
            cacheamount = checkGoldTotal(i)
            embed2.add_field(name=f'CacheNinja{i}', value=str(cacheamount))
          await msg.edit(content="Done processing.", embed=embed2)
          memberamount = setmember(member.id, amount)
          await ctx.send(f'<@{member.id}>\'s new monthly total is {memberamount}. You may now close the ticket.')
        else:
          embed2 = discord.Embed(color=Color.green(), title = 'Failed. Below are the target amounts based on the entered amount.')
          for i in cachelist:
            cacheamount = cachelist[i]
            embed2.add_field(name=f'CacheNinja{i}', value=str(cacheamount))
          await msg.edit(content="Done processing.", embed=embed2)
    
    @commands.command(help='Sync the Cache to their fetched numbers.', aliases=['c_sync','csync'])
    @commands.has_any_role(702011263680643173, 935919659872567366)
    async def cachesync (self, ctx):
      msg = await ctx.send('Please confirm that you want to match the values. \n**THIS CANNOT BE UNDONE!**')
      await msg.add_reaction("✅")
      def check(reaction, user):
            return str(reaction.emoji) == "✅" and user.id == ctx.author.id and reaction.message.id == msg.id
      while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=120.0, check=check)
            except Exception:
                await msg.edit(content='This action has been canceled.')
            if str(reaction.emoji) == "✅" and user.id == ctx.author.id:
              await msg.edit(content='Approved. Proccessing....')
              #fetch the current gold amounts and set the stored values to match
              for x in range(5):
                setcache(x+1, checkGoldTotal(x+1))
              #output new amounts
              embed = Embed(color=Color.green(), title='Updated cache amounts')
              t = 0
              for i in range(5):
                  cacheamount = get_amount(i+1)
                  t+=cacheamount
                  embed.add_field(name=f'CacheNinja{i+1}', value=str(cacheamount))
              embed.description = 'Total collected = ' + str(t)
              await msg.edit(content="Updated!", embed=embed)
              break              

async def setup(bot):
  await bot.add_cog(Donations(bot))