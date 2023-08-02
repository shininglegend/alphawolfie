import psycopg2 as pgsql
import discord

#0 = on my machine, 1 = on digital ocean
with open('location.txt', 'r') as f:
    location = int(f.read())
    f.close()
    
MY_GUILD = discord.Object(id=468176956232302603)

conn = pgsql.connect("dbname=alphawolfie user=postgres password=password")
curr = conn.cursor()

def is_it_me(ctx):
    return ctx.message.author.id == 585991293377839114