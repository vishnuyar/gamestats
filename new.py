# bot.py
import os
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands
from game import Game, Register, Player, Winner
from connect import Connection


try:
    load_dotenv()
    TOKEN=os.getenv('DISCORD_TOKEN')
    GUILD=os.getenv('DISCORD_GUILD')
    CHANNEL="pokerstats"
    connect=Connection()
    connect.connect()

    bot=commands.Bot(command_prefix = '!')

    @ bot.command(name = 'buy')
    async def buy(ctx, *args):
        if (ctx.channel.name == CHANNEL):
            game=Game(connect)
            response=game.addBuyins(args)
            await ctx.send(response)

    @ bot.command(name = 'winner')
    async def winner(ctx,*args):
        if (ctx.channel.name == CHANNEL):
            if (len(args) ==2):
                response=Winner(connect).normalWin(args[0],args[1])
            else:
                response = "You need two winners"
            await ctx.send(response)

    @ bot.command(name = 'game')
    async def game(ctx):
        if (ctx.channel.name == CHANNEL):
            response = Game(connect).getStatus()
            await ctx.send(response)
    
    @ bot.command(name = 'rank')
    async def rank(ctx):
        if (ctx.channel.name == CHANNEL):
            response = Game(connect).getRank()
            await ctx.send(response)

    @ bot.command(name = 'start')
    async def start(ctx, *args):
        if (ctx.channel.name == CHANNEL):
            game=Game(connect).newGame(*args)
            response=f"Started new game {game[0]} at {game[1]}"
            await ctx.send(response)

    @ bot.command(name = 'register')
    async def register(ctx, arg):
        if (ctx.channel.name == CHANNEL):
            players=Game(connect).getPlayers()
            name=arg
            if name.lower() in players:
                response=f"{name} is already a registered player"
            else:
                result=Register(connect).addPlayer(name.lower())
                if result:
                    response=f"you have registered player {result}"
                else:
                    response=f"Unable to register {name}"
            await ctx.send(response)

    bot.run(TOKEN)
except Exception as e:
    print(e)
finally:
    connect.close()
