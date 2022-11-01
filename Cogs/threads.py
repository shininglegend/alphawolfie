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