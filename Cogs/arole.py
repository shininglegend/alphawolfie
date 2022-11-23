import discord, datetime
from discord.ext import commands
#from replit import db
from discord import Embed, Color
import tracemalloc

tracemalloc.start()


rolelist={902946790410706964: 'red',
    902945846063153222: 'black',
    902946416442376223: 'purple',
    902945721144205332: 'yellow',
    902946088972070942: 'brown',
    902946619589279777: 'orange',
    902945517762408508: 'pink',
    902946028611862598: 'white',
    902946218613813279: 'blue'}

def is_it_me(ctx):
    return ctx.message.author.id == 585991293377839114

class ColorButton(discord.ui.Button['ColorView']):
    def __init__(self, roleid = int, rolenum = int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f'{rolenum}', custom_id=f'colorroles{roleid}')
        self.roleid = roleid


    async def log0101(self, message, guild, title="Logged Event:"):
      cha = await guild.fetch_channel(777042897630789633)
      embed3 = Embed(title=title, description=message, color=Color.green(), timestamp=datetime.datetime.now())
      await cha.send(embed=embed3)

    async def addrole(self, interaction, roleid):
        role2 = interaction.guild.get_role(roleid)
        nusr = interaction.user
        if role2 in nusr.roles:
            await interaction.response.send_message(content=f'Your color role has been removed', ephemeral=True)
            await nusr.remove_roles(role2)
            await self.log0101(f"Removed <@&{role2.id}> from <@{nusr.id}>", interaction.guild)
        else:
            await interaction.response.send_message(content=f'Your color role is now  <@&{role2.id}>, please wait for it to update.', ephemeral=True)
            rolelist2 = []
            rolelist3 = []
            for role3 in rolelist:
              #print(f'{role3} : {role2.id} = {role3 == role2.id}')
              role3 = interaction.guild.get_role(role3)
              rolelist2.append(role3)
              rolelist3.append(role3.id)
            #rolelist2 = tuple(rolelist2)
            #for role5 in rolelist2:
            await nusr.remove_roles(* rolelist2)
            await nusr.add_roles(role2)
            await self.log0101(f"Added <@&{role2.id}> to <@{nusr.id}>", interaction.guild)
            r3 = ''
            for r in rolelist3:
              r3 += f'<@&{r}> '
            await self.log0101(f"Removed {r3} from <@{nusr.id}>", interaction.guild)
            

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        #view: Colorview = self.view
        #await interaction.response.defer(ephemeral=True)
        print(f'{rolelist[self.roleid]} pressed.')
        await self.addrole(interaction, roleid=self.roleid)
        

class ColorView(discord.ui.View):
    
    def __init__(self):
        super().__init__(timeout=None)
        i=0
        for roleid2 in rolelist:
          i+=1
          self.add_item(ColorButton(roleid2, i))

    

class Arole(commands.Cog):
    def __init__(self, bot):
      self.bot = bot
      self.persistent_views_added = False
      self.description = 'These commands handle roles. They can be safely ignored.'

    async def log0101(self, message, title=None):
      cha = await self.bot.fetch_channel(777042897630789633)
      if not title:
        title="Logged Event:"
      embed3 = Embed(title=title, description=message, color=Color.green(), timestamp=datetime.datetime.now())
      await cha.send(embed=embed3)
    #events

    @commands.Cog.listener()
    async def on_ready(self):
      print('Arole is online')
      if not self.persistent_views_added:
        self.bot.add_view(ColorView())
        self.persistent_views_added = True
        print('Added ColorView')

    #commands
    @commands.command(help='colormsg')
    @commands.check(is_it_me)
    async def colormsg(self, ctx): 
        msg2 = ''
        i = 0
        for color1 in rolelist:
            i+=1
            msg2 += f'**{i}** : *<@&{color1}>*\n'
        embed3= Embed(color=Color.dark_grey(), title = "__Pick your roles below!:__", description = msg2)
        await ctx.message.delete()
        await ctx.send(embed=embed3, view=ColorView())

async def setup(bot):
   await bot.add_cog(Arole(bot))
  