import discord, os, sys, json, random, logging, time, datetime
#from keep_alive import keep_alive
from discord.ext import commands
#from replit import db
from discord import Embed, Color, ui, app_commands
#import sqlite3
from typing import Literal, Optional
from discord.ext.commands import Greedy, Context
from discord.member import VoiceState

from helpers.client import MyClient
from helpers.verify import PersistentView
from helpers.help import MyHelp
from init import location

if location == 0:
  myprefix = '>'
else:
  myprefix = ';'


client = MyClient(command_prefix=myprefix,intents = discord.Intents.all(), case_insensitive=True) #switch prefix!
client.help_command = MyHelp(client=client) # set our help command to our custom one


try:
  if location == 0: 
    f = open("key.txt", 'r')
    key = f.read()
    client.run(key) #switch prefix!!
  else: client.run(os.getenv("DISCORD_TOKEN"))
except Exception:
  exep = sys.exc_info()
  expv = exep[1]
  print('Failed to start:\n%s'%(str(expv)))