from logging import exception
from typing import Text
import discord
from discord import user
from discord import guild
from discord.ext import tasks
from discord.ext import commands
from discord.ext.commands import bot
from discord.ext.commands.core import command
from discord.utils import get
import os



from urllib.request import urlopen,Request
from bs4 import BeautifulSoup as soup
from googlesearch import search
import datetime

import pymongo
from pymongo import DESCENDING, MongoClient

cluster = MongoClient(
    "mongodb link goes here"
)
db = cluster["AblioDB"]
collection = db["Splits"]


intents = discord.Intents.default()
client = commands.Bot(command_prefix='!!', intents=discord.Intents.all())

global reactIds
dtbase = collection.find({})
reactIds = []
for el in dtbase:
    reactIds.append(el["embedID"])

global roleMsgId
roleMsgId = 0000 #id removed from code

global roleReactions
roleReactions = []

global roleIds
roleIds = []

@client.event
async def on_ready():
    global roleMsgId
    global roleReactions
    global roleIds

    g = client.get_guild(0000) #id removed from code
    roleChan = g.get_channel(0000) #id removed from code
    roleMessage = await roleChan.fetch_message(roleMsgId)

    lines = roleMessage.content.split("\n")
    for x in lines:
        things = x.split(": ")
        roles = things[0][3:-2]
        #print(roles)
        reaction = things[1]
        await roleMessage.add_reaction(reaction)
        roleReactions.append(reaction)
        roleIds.append(roles)
    print('Bot is ready.')


@client.event
async def on_raw_reaction_add(payload):
    global reactIds
    global roleMsgId
    global roleIds
    g = client.get_guild(0000) #id removed from code


    if payload.message_id in reactIds:
        chan = g.get_channel(payload.channel_id)
        member = payload.member
        message = await chan.fetch_message(payload.message_id)
        if (member.id!=0000) : #id removed from code
            await message.remove_reaction(payload.emoji,member)

            embed = message.embeds[0]
            embed_dict = embed.to_dict()
            for field in embed_dict["fields"]:
                if field["name"] == member.name:
                    field["value"] = "Claimed ✅"
            
            completed = 1
            for field in embed_dict["fields"]:
                if "Unclaimed" in field["value"]:
                    completed = 0
            
        
            embed = discord.Embed.from_dict(embed_dict)

            if (completed==1):
                embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Checkmark.svg/1200px-Checkmark.svg.png")
                embed.title="✅ Completed Split ✅"
                collection.delete_one({'_id': payload.message_id})
                print("Split with id {} is done and has been removed from the database".format(payload.message_id))

            await message.edit(embed=embed)
    elif payload.message_id == roleMsgId:
        print("hoho")
        for i in range(len(roleReactions)):
            if payload.emoji.name == roleReactions[i]:
                #print("role added")
                r = discord.utils.get(g.roles, id=int(roleIds[i]))
                await payload.member.add_roles(r)
                
        

@client.event
async def on_raw_reaction_remove(payload):
    global reactIds
    global roleMsgId
    global roleIds
    g = client.get_guild(188976143871901696)

    if payload.message_id == roleMsgId:
        for i in range(len(roleReactions)):
            if payload.emoji.name == roleReactions[i]:
                print("role remove")
                print(roleIds[i])
                r = discord.utils.get(g.roles, id=int(roleIds[i]))
                member = discord.utils.get(g.members, id=payload.user_id)
                await member.remove_roles(r)


@client.command()
async def hello(ctx):
    await ctx.send('Hello Friend')
    


@client.command()
async def mysplits(ctx):
    g = client.get_guild(188976143871901696)
    chan = g.get_channel(683323340223807518)
    u = client.get_user(ctx.author.id)
    msg = await u.send("yo")

    allSplits = collection.find({})
    flag = False

    for split in allSplits:
      people = split["people"]
      if ctx.author.id in people:
        message = await chan.fetch_message(split["embedID"])
        embed = message.embeds[0]
        embed_dict = embed.to_dict()

        for field in embed_dict["fields"]:
          if field["name"] == u.name and not field["value"] == "Claimed ✅":
            flag = True
            splitter = g.get_member(split["author"])
            msg = await u.send(str(split["split"] + " by " + str(splitter.name)))

    if not flag:
        msg= await u.send("No one owes you money, yayyy")
        

@client.command()
async def forcecomplete(ctx,msgid:int,chid:int=0000,gid:int=0000): #ids removed
    g = client.get_guild(gid)
    chan = g.get_channel(chid)
    message = await chan.fetch_message(msgid)
    embed = message.embeds[0]
    embed_dict = embed.to_dict()

    for field in embed_dict["fields"]:
        field["value"] = "Claimed ✅"

    embed = discord.Embed.from_dict(embed_dict)
    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Checkmark.svg/1200px-Checkmark.svg.png")
    embed.title="✅ Completed Split ✅"
    collection.delete_one({'_id': msgid})
    print("Split with id {} is done and has been removed from the database".format(msgid))

    await message.edit(embed=embed)

@client.command()
async def split(ctx,money,*args: discord.User):
    global reactIds

    ids = []
    for arg in args:
        ids.append(arg.id)

    embed = discord.Embed(title=':moneybag:  Loot Split  :moneybag: ',description=str(money + " each"),colour=discord.Colour.red())
    #embed.set_author(name=ctx.author.display_name,icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url=ctx.author.avatar_url)
    for arg in args:
        embed.add_field(name=arg.name,value="Unclaimed :x:")

    msg = await ctx.send(embed=embed)
    await msg.add_reaction("✅")

    post = {
            "_id": msg.id,
            "split": money,
            "author": ctx.author.id,
            "people": ids
        }
        
    collection.insert_one(post)

    if msg.id not in reactIds:
        reactIds.append(msg.id)

@client.command()
async def clean(ctx,msgID):
    try:
        result = collection.delete_one({'_id': msgID})
        await ctx.send("Split " + msgID + " has been completed and was removed from the database")
    except exception as e:
        print(e)


@client.command(aliases=['ds'])
async def dndsearch(ctx,*,query):
    success = 1
    url = 'no'
    query = 'site:dnd5e.wikidot.com ' + query
    for j in search(query, tld="com", num=1, stop=1, pause=0):
        print(j)
        url = j
        
    if not "wikidot.com" in url:
            print("no results")
            await ctx.send("No results matching this search query")
            success = 0
    try:
        if success == 1:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            uClient = urlopen(req)
            page_html = uClient.read()
            uClient.close()
            page_soup = soup(page_html, "html.parser")

            containers = page_soup.findAll("div",{"class":"page-title page-header"})
            title = containers[0].text
            title = '**' + title + '**'

            containers = page_soup.findAll("div",{"id":"page-content"})
            content = containers[0].text

            bigstring = title + content + 'Source: ' + url

            await ctx.send(bigstring)
    except Exception as e:
        print(e)
        await ctx.send("The page is probably too big to fit in discord chat, here's the link of the page: " + url)


@client.command()
async def deletepm(ctx, id):
    msg = await ctx.fetch_message(id)
    await msg.delete()

@client.command()
async def pm_person(ctx,id:int,*,message):
    u = client.get_user(id)
    msg = await u.send(message)
    print("message sent to {}".format(u.display_name))

@client.command()
async def dnd_announcement(ctx,*,message):
    g = client.get_guild(0000) #ids, removed once again
    role = g.get_role(0000)
    for member in role.members:
        await member.send(message)
        print("message sent to {}".format(member.display_name))

@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')

@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')

@client.command()
async def reload(ctx, extension=None):
    if extension != None:
        client.unload_extension(f'cogs.{extension}')
        client.load_extension(f'cogs.{extension}')
        await ctx.send("Reloaded " + str(extension))
    else:
        await ctx.send("Reloading all cogs")
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    client.unload_extension(f'cogs.{filename[:-3]}')
                    client.load_extension(f'cogs.{filename[:-3]}')
                except:
                    print("exception occured while reloading cogs, its probably nothing tho")
        await ctx.send("Reloaded all cogs")
    

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.remove_command("help")


client.run('bot token, removed from code')