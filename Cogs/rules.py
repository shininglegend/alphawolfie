# This handles adding/removing rules as needed
"""
Task list: TODO
- Allow rules to be grouped by section
    [X] Add section column to database
    [ ] Add section to embed
    [X] Add section to add_rule command
    [X] Add section to remove_rule command
    [ ] Add section to update_rule command
    [ ] Add section to mass_update_rules command
    [ ] Add section to rules_msg command
    [ ] Add section to send_rules command
    [ ] Add section to rule command
- Add details to an existing rule by number
    [X] Add details column to database
    [ ] Add details to embed
    [ ] Add details to add_rule command
    [ ] Add details to update_rule command
    [ ] Add details to mass_update_rules command
    [ ] Add details to rules_msg command
    [ ] Add details to send_rules command
    [ ] Add details to rule command
"""
import discord
from discord.ext import commands

from discord import Embed
#import sqlite3
import psycopg2 as pgsql

from init import conn, curr, location, is_it_me
from Cogs.staff_only import is_admin

# Rules channel
if location == 0:
    RULES_CHA = 960621959211798699
else:
    RULES_CHA = 670361959345946657


# Reset the table
def reset_rules(rules):
    curr.execute('DROP TABLE IF EXISTS rules')
    curr.execute('CREATE TABLE IF NOT EXISTS rules (id SERIAL PRIMARY KEY, rule TEXT NOT NULL, details TEXT, section INTEGER DEFAULT 0)')
    if rules:
        for rule in rules:
            # Insert the rule into a new row, assuming the data is transfered over exactly
            curr.execute('INSERT INTO rules (rule, details, section) VALUES (%s, %s, %s)', (rule[1], rule[2], rule[3]))
        conn.commit()

# Grab the rules from the database
def get_rules(id = None, rule = None, details = None, section = None):
    if id:
        curr.execute('SELECT * FROM rules WHERE id = %s', (id,))   
    elif rule:
        curr.execute('SELECT * FROM rules WHERE rule = %s', (rule,))       
    elif details:
        curr.execute('SELECT * FROM rules WHERE details = %s', (details,))
    elif section:
        curr.execute('SELECT * FROM rules WHERE section = %s', (section,))
    else:
        curr.execute('SELECT * FROM rules ORDER BY id ASC')
    if curr.rowcount == 0:
        return None
    return curr.fetchall()

def get_rule_by_search(rule_search):
    curr.execute('SELECT * FROM rules WHERE rule LIKE %s', ('%'+rule_search+'%',))
    if curr.rowcount == 0:
        return None
    return curr.fetchone()

def get_rule_disc(rule):
    curr.execute('SELECT rule FROM rules WHERE id = %s', (rule,))
    if curr.rowcount == 0:
        return None
    return curr.fetchone()[0]

#print(get_rules())
# Add rules to the database
def add_rules(rules):
    for rule in rules:
        insert_rule(rule)


def insert_rule(rule, details=None, section=None):
    rule = rule.replace("'", "''")
    curr.execute('INSERT INTO rules (rule, details, section) VALUES (%s, %s, %s)', (rule, details, section))
    conn.commit()

# Update a rule in the database
def update_rule(number, rule, details=None, section=None):
    curr.execute('UPDATE rules SET rule = %s, details = %s, section = %s WHERE id = %s', (rule, details, section, number))
    conn.commit()

# Delete a rule from the database
def delete_rule(number):
    curr.execute('DELETE FROM rules WHERE id = %s', (number,))
    rules = get_rules()
    reset_rules(rules)


# Rules commands
class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = 'Get the rules for the server!'
        
    
    def on_ready(self):
        print('Rules is online')
        
    # This function sends the rules embed to a channel (called by multiple commands)
    async def send_rules(self, ctx, channel):
        #print(channel)
        await channel.typing()
        await channel.purge(limit=2, check=lambda m: m.author == self.bot.user)
        rules = get_rules()
        #print(rules)
        descript = ''
        if not rules:
            await channel.send('There are no rules set yet.')
            return
        # Reset the numbering if it's off
        if rules[0][0] != 1:
            reset_rules(get_rules())
            rules = get_rules()
        for rule in rules:
            if not rule[1]:
                print(f'Rule {rule[0]} is empty')
                continue
            disc = rule[1].replace("''", "'")
            descript += str(rule[0]) + ': ' + disc + '\n\n'
            # Future code to handle sections will go here
            
        embed = Embed(color=1075714,
                    title='Ninja.io Discord rules:', 
                    description="--------------" + '\n' + descript + "--------------\n\n**Violation of these rules can result in a warn, mute, kick or ban.**",
                    timestamp=ctx.message.created_at)
        embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/756567998570954903.png?v=1')
        await channel.send(embed=embed)

    # Confirm an operation via reaction
    async def confirm(self, ctx, msg, timeout=10.0):
        await msg.add_reaction('✅')
        await msg.add_reaction('❌')
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['✅', '❌']
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=timeout, check=check)
            if str(reaction.emoji) == '❌':
                await ctx.reply('Operation cancelled.')
                return False
        except:
            await ctx.reply('Timed out. Operation cancelled.')
            return False
        return True

    # Get a specific rule by number
    @commands.hybrid_command(help='Get a specific rule by number or text', aliases=['r, rules, getrule, gr'])
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def rule(self, ctx, rule):
        await ctx.defer()
        # If it's a number:
        if rule.isdigit():
            rule = get_rules(id=int(rule))
        else:
            rule = get_rule_by_search(rule)
        if not rule:
            await ctx.send('That rule was not found.')
            return
        # TODO: Need to add section and details if they exist
        await ctx.send("📖 " + str(rule[0]) + ". " + rule[1])
    
    # Send the rules embed, admin only (channel id is 670361959345946657)
    @commands.command(help='Send the rules embed, Admin only', aliases=['sendrules'])
    @commands.check(is_admin)
    async def rules_msg(self, ctx, channel: discord.TextChannel=None):
        if not channel:
            channel = await ctx.guild.fetch_channel(RULES_CHA)
        if not channel:
            await ctx.reply('Channel not found.')
            return
        await ctx.channel.typing()
        await self.send_rules(ctx, channel)
        await ctx.send('Rules sent!')

    # Mass update the rules
    @commands.command(help='Mass update the rules, Dev only')
    @commands.check(is_it_me)
    async def mass_update_rules(self, ctx, *, rules):
        await ctx.channel.typing()
        rules = rules.split('\n')
        # Reset the table, passing no rules so it's empty
        reset_rules(None)
        for rule in rules:
            #print(rule)
            rule = rule.replace("'", "''")
            # Remove the number from the rule
            #rule = rule[rule.find(':')+2:]
            # ignore empty rules
            if not rule or rule == ' ' or rule == "\n":
                continue
            # TODO: Add section and details if they exist
            insert_rule(rule)
        channel = await ctx.guild.fetch_channel(RULES_CHA)
        await self.send_rules(ctx, channel)
        await ctx.reply('Rules updated!') 

    # Update a rule
    @commands.command(help='Update a rule by rule number, Admin only')
    @commands.check(is_admin)
    async def update_rule(self, ctx, rule: int, *, new_rule):
        # Confirm they want to update the rule via reaction
        rule_disc = get_rule_disc(rule)
        #print(curr.rowcount)
        #print(curr.fetchone())
        if not rule_disc:
            await ctx.reply('That rule was not found.')
            return
        msg = await ctx.reply(f'Are you sure you want to update rule {rule}: {rule_disc}?')
        if not await self.confirm(ctx, msg):
            await ctx.reply('Cancelled.')
            return

        # Update the rule (and the x reaction)
        await msg.remove_reaction('❌', self.bot.user)
        await msg.edit(content='Updating rules...')
        new_rule = new_rule.replace("'", "''")
        update_rule(rule, new_rule)      
        # Send the rules embed
        channel = await ctx.guild.fetch_channel(RULES_CHA)
        await self.send_rules(ctx, channel)
        await msg.edit(content='Rule updated, and rules list updated!')

    # Add a rule
    @commands.command(help='Add a rule, Admin only')
    @commands.check(is_admin)
    async def add_rule(self, ctx, *, rule):
        if not rule:    
            await ctx.reply('Please specify a rule.')
            return
        details = None
        if "|" in rule:
            rule, details = rule.split("|")
            rule = rule.strip()
            details = details.strip()

        # Add the rule
        insert_rule(rule, details)
        channel = await ctx.guild.fetch_channel(RULES_CHA)
        await self.send_rules(ctx, channel)
        await ctx.reply('Rule added!')

    # Remove a rule
    @commands.command(help='Remove a rule by rule number, Admin only')
    @commands.check(is_admin)
    async def remove_rule(self, ctx, rule: int):
        # Confirm they want to remove the rule via reaction
        rule_disc = get_rule_disc(rule)
        if not rule_disc:
            await ctx.reply('That rule was not found.')
            return
        msg = await ctx.reply(f'Are you sure you want to remove rule {rule}: {rule_disc}?')
        if not await self.confirm(ctx, msg):
            await ctx.reply('Cancelled.')
            return
        
        # Remove the rule (and the x reaction)
        await msg.remove_reaction('❌', self.bot.user)
        delete_rule(rule)
        await msg.edit(content='Rule removed! Updating rules...') 
        # Send the rules embed
        channel = await ctx.guild.fetch_channel(RULES_CHA)
        await self.send_rules(ctx, channel)
        await msg.edit(content='Rule removed! Rules updated!')


async def setup(bot):
    await bot.add_cog(Rules(bot))
