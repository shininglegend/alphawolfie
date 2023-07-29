## This doesn't do anything :P And likely won't ever. I just wanted to see if I could make a cog that didn't do anything. I can. I did. I'm happy. :D
# Jk it was meant to be useful once upon a time, but I never got around to it. I'll probably delete it eventually. Or not. Who knows. I'm not a psychic. I'm just a programmer. :P

import discord, os, sys, json, random, logging, requests
from discord.ext import commands
#from replit import db
from discord import Embed, Color


class Threads(commands.Cog):
    def __init__(self, bot):
      self.bot = bot

    #events
    @commands.Cog.listener()
    async def on_ready(self):
      print('threads is online')




async def setup(bot):
  await bot.add_cog(Threads(bot))