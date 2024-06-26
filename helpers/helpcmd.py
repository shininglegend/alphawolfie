import datetime, contextlib
from discord.ext import commands
from discord import Color, Embed

class HelpEmbed(Embed): # Our embed with some preset attributes to avoid setting it multiple times
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timestamp = datetime.datetime.utcnow()
        text = "Use help [command] or help [category] for more information | <> is required | [] is optional"
        self.set_footer(text=text)
        self.color = Color.dark_green()
        

class MyHelp(commands.HelpCommand):
    def __init__(self, client):
      super().__init__( # create our class with some aliases and cooldown
            command_attrs={
                "help": "The help command for the bot",
                "aliases": ['commands',"helps", "helpme", "h"],
                "case_insensitive" : True
            }
        )
      self.client = client # set our client to the one we defined in main.py

    def get_command_signature(self, command):
        return '%s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)

    async def send(self, **kwargs):
        """a short cut to sending to get_destination"""
        await self.get_destination().send(**kwargs)

    async def send_bot_help(self, mapping):
        """triggers when a `<prefix>help` is called"""
        ctx = self.context
        embed = HelpEmbed(title=f"{ctx.me.display_name} Help")
        embed.set_thumbnail(url=ctx.me.display_avatar)
        usable = 0 
        for cog, commands in mapping.items(): #iterating through our mapping of cog: commands
            if filtered_commands := await self.filter_commands(commands): 
                # if no commands are usable in this category, we don't want to display it
                if len(filtered_commands) == 0:
                    continue
                amount_commands = len(filtered_commands)
                usable += amount_commands
                if cog: # getting attributes dependent on if a cog exists or not
                    name = cog.qualified_name
                    description = cog.description or "There's no info on these commands. Yet."
                embed.add_field(name=f"{name} Category", value=f'`{amount_commands} usable`\n{description}')
        embed.description = f"{usable} commands you can use." 
        await self.send(embed=embed)

    async def send_command_help(self, command):
        """triggers when a `<prefix>help <command>` is called"""
        signature = self.get_command_signature(command) # get_command_signature gets the signature of a command in <required> [optional]
        embed = HelpEmbed(title=signature, description=command.help or "No help found...")
        if cog := command.cog:
            embed.add_field(name="Category", value=cog.qualified_name)
        can_run = "No"
        # command.can_run to test if the cog is usable
        with contextlib.suppress(commands.CommandError):
            if await command.can_run(self.context):
                can_run = "Yes"           
        embed.add_field(name="Usable", value=can_run)
        if command._buckets and (cooldown := command._buckets._cooldown): # use of internals to get the cooldown of the command
            embed.add_field(
                name="Cooldown",
                value=f"{cooldown.rate} per {cooldown.per:.0f} seconds",)
        #await self.send(embed=embed)
        if isinstance(command, commands.Group) and (filtered_commands := await self.filter_commands(command.commands)):
            for subcommand in filtered_commands:
                embed.add_field(name=self.get_command_signature(subcommand), value=subcommand.help or "No help found...")
        await self.send(embed=embed)

    async def send_help_embed(self, title, description, commands): # a helper function to add commands to an embed
        embed = HelpEmbed(title=title, description=description or "No help found...")
        if filtered_commands := await self.filter_commands(commands):
            for command in filtered_commands:
                embed.add_field(name=self.get_command_signature(command), value=command.help or "No help found...")
        await self.send(embed=embed)

    async def send_cog_help(self, cog):
        title = cog.qualified_name or "Developer"
        await self.send_help_embed(f'{title} Category', cog.description, cog.get_commands())

    async def send_group_help(self, group):
        """triggers when a `<prefix>help <group>` is called"""
        title = self.get_command_signature(group)
        await self.send_help_embed(title, group.help, group.commands)
    
    async def command_not_find(self):
        await self.send_help_embed(f'That command or category was not found.')