import discord, random

#define stuff
def randomtopic():
  l = []
  with open('randomtopics.txt') as f:
    for line in f: 
      l.append(line)
  return random.choice(l)


class PersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Agree and Verify!', style=discord.ButtonStyle.green, custom_id='verifybutton')
    async def verify(self,  interaction: discord.Interaction, button: discord.ui.Button):
        print("seen")
        await interaction.response.send_message(content='You have sucessfully verified. Say hi in <#670362292659159040>!', ephemeral=True)
        nusr = interaction.user
        role1 = interaction.guild.get_role(702710000048668783)
        await nusr.add_roles(role1)
        print("added role")
        channel = interaction.guild.get_channel(670362292659159040)
        await channel.send(f'Welcome, <@{nusr.id}> as the {interaction.guild.member_count}th user!')
        await channel.send(f'~{randomtopic()}')  