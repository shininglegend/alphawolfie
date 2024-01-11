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

# Initial setup, will remove later
#curr.execute('DROP TABLE IF EXISTS rules')
curr.execute('CREATE TABLE IF NOT EXISTS rules (id SERIAL PRIMARY KEY, rule TEXT NOT NULL, details TEXT, section INTEGER DEFAULT 0)')
conn.commit()
# Add the rules to the database if they aren't already there
def add_rules(rules):
    curr.execute('SELECT * FROM rules')
    if curr.rowcount == 0:
        for rule in rules:
            # Remove the number from the rule
            rule = rule[rule.find('.')+2:]
            # Escape single quotes
            rule = rule.replace("'", "''")
            if not rule:
                continue
            curr.execute('INSERT INTO rules (rule) VALUES (%s)', (rule,))
        conn.commit()

rules = ["No spamming or flooding the chat with messages.",
"No hate comments. Just respect everyone else, friendly debates are ok.",
"No adult (18+), explicit, graphic content.",
"No racist or degrading content.",
"No excessive cursing.",
"No advertising other sites/discord servers.",
"No begging or repeatedly asking for help in the chat, just DM a staff member.",
"Post content in the designated channels.",
"Do not promote the intentional use of glitches, hacks, or bugs.",
"Do not cause a nuisance in the community, repeated complaints from several members will lead to administrative action.",
"Arguing or disrespect to staff members can and often will result in an instant ban. If you feel you have been wrongly treated, DM a higher-ranked staff member and ask for help.",
"Don't post someone's personal information without their permission.",
"Follow Discord TOS: https://discordapp.com/terms",
"Don't ping staff unless you have a good reason, doing so will result in a mute.",
"Don't DM staff with questions about game updates / ETA's / suggestions etc. Updates and release dates will be announced in the <#670362003356778498> channel, while suggestions belong in the <#670362431373180948> channel.",
"No political banners or slogans allowed. Do not politicize the server.",
"Impersonating staff or any other member is prohibited.",
"Using alt accounts to bypass a punishment is not allowed.",
"No 'dead chat' comments. There will be times when people don't chat. No need to remind everyone.",
"Spreading false information, posting disturbing, misleading or political media /messages, and posting age-restricted content is not allowed.",
"Your actions outside this discord will now also affect whether or not you are allowed inside the discord. You are still the same person, and we will not tolerate any raid/DDoS/death threats, or any major violation of the rules in ninja.io or any major social media site.",
"This server is English only for moderation purposes."]
add_rules(rules)
# End initial setup

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
def get_rules():
    curr.execute('SELECT * FROM rules')
    return curr.fetchall()


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

    # Get a specific rule by number
    @commands.hybrid_command(help='Get a specific rule by number or text', aliases=['r, rules, getrule, gr'])
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def rule(self, ctx, rule):
        await ctx.defer()
        rule = curr.execute('SELECT * FROM rules WHERE id = %s', (rule,))
        if curr.rowcount == 0:
            # Attempt a text search
            curr.execute('SELECT * FROM rules WHERE rule LIKE %s', ('%'+rule+'%',))
            if curr.rowcount == 0:
                await ctx.send('That rule was not found.')
                return
        rule = curr.fetchone()
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
            curr.execute('INSERT INTO rules (rule) VALUES (%s)', (rule,))
        conn.commit()
        channel = await ctx.guild.fetch_channel(RULES_CHA)
        await self.send_rules(ctx, channel)
        await ctx.reply('Rules updated!') 

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
        # Get the number of rules
        curr.execute('SELECT * FROM rules')
        # Add the rule
        rule = rule.replace("'", "''")
        curr.execute('INSERT INTO rules (rule, details) VALUES (%s, %s)', (rule, details))
        conn.commit()
        channel = await ctx.guild.fetch_channel(RULES_CHA)
        await self.send_rules(ctx, channel)
        await ctx.reply('Rule added!')

    # Remove a rule
    @commands.command(help='Remove a rule by rule number, Admin only')
    @commands.check(is_admin)
    async def remove_rule(self, ctx, rule: int):
        # Confirm they want to remove the rule via reaction
        curr.execute('SELECT rule FROM rules WHERE id = %s', (rule,))
        if curr.rowcount == 0:
            await ctx.reply('That rule was not found.')
            return
        rule_disc = curr.fetchone()[0]
        msg = await ctx.reply(f'Are you sure you want to remove rule {rule}: {rule_disc}?')
        await msg.add_reaction('✅')
        await msg.add_reaction('❌')
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['✅', '❌']
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
            if str(reaction.emoji) == '❌':
                await ctx.reply('Rule not removed.')
                return
        except:
            await ctx.reply('Timed out. Operation cancelled.')
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
