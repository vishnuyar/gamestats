# bot.py
from os import getenv
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands
from game import Game, Register, Player, Winner
from connect import Connection
from data import Details
from image import createImage


try:
    load_dotenv()
    # TOKEN=getenv('DISCORD_TOKEN')
    # GUILD=getenv('DISCORD_GUILD')
    TOKEN=Details().DISCORD_TOKEN
    GUILD=Details().DISCORD_GUILD
    
    CHANNEL="pokerstats"
    connect=Connection()
    connect.connect()

    bot=commands.Bot(command_prefix = '!')

    @ bot.command(name = 'buy',help="'playername': Add as many players names as buyins ")
    async def buy(ctx, *args):
        if (ctx.channel.name == CHANNEL):
            game=Game(connect)
            response=game.addBuyins(args)
            await ctx.send(response)

    @ bot.command(name = 'winner',help="'winnername' 'runnername'")
    async def winner(ctx,*args):
        if (ctx.channel.name == CHANNEL):
            if (len(args) ==2):
                response=Winner(connect).normalWin(args[0],args[1])
            else:
                response = "You need two winners"
            await ctx.send(response)

    @ bot.command(name = 'icm',help="'winnerchips/runnerchips' 'winner/runner'")
    async def icm(ctx,*args):
        if (ctx.channel.name == CHANNEL):
            if (len(args) ==2):
                response=Winner(connect).ICMWin(args[0],args[1])
            else:
                response = "You need to provide both chip counts and winners"
            await ctx.send(response)


    @ bot.command(name = 'game',help="Will give the current status of the game")
    async def game(ctx):
        if (ctx.channel.name == CHANNEL):
            response = Game(connect).getStatus()
            await ctx.send(response)
    
    @ bot.command(name = 'rank',help="'text' Will give the Leaderboard for the current year")
    async def rank(ctx,*arg):
        if (ctx.channel.name == CHANNEL):
            if arg:
                await ctx.send("\n".join(Game(connect).getRank()))
            else:
                createImage()
                await ctx.send(file=discord.File('rank.png'))

    @ bot.command(name = 'start',help="'buyin amount' 'rent' Default is 400,200")
    async def start(ctx, *args):
        if (ctx.channel.name == CHANNEL):
            game=Game(connect).newGame(*args)
            response=f"Started new game {game[0]} at {game[1]}"
            await ctx.send(response)

    @ bot.command(name = 'register',help="'playername' for adding a new player to the System")
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
