import discord, os
#from keep_alive import keep_alive
#from replit import db
#import sqlite3


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


#try:
client.run(os.environ.get("DISCORD_TOKEN"))
#   pass
# except Exception:
#   exep = sys.exc_info()
#   expv = exep[1]
#   print('Failed to start:\n%s'%(str(expv)))