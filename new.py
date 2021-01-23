# bot.py
from os import getenv
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands
from game import Game, Register, Player, Winner
from expense import Expense
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
            if len(args) > 0:
                game=Game(connect)
                response=game.addBuyins(args)
            else:
                response="Add player names for buyins"
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

    @ bot.command(name = 'expense',help="Add expense details amount, description")
    async def game(ctx,*args):
        if (ctx.channel.name == CHANNEL):
            if len(args) > 1:
                response = Expense(connect).add(args)
            else:
                response = "Both Amount and description required for adding expense"
            await ctx.send(response)
    
    @ bot.command(name = 'balance',help="Gives reserve fund balance")
    async def balance(ctx,*args):
        if (ctx.channel.name == CHANNEL):
            response = Expense(connect).balance()
            await ctx.send(response)
    
    @ bot.command(name = 'rank',help="'text' Will give the Leaderboard for the current year")
    async def rank(ctx,*arg):
        if (ctx.channel.name == CHANNEL):
            if arg:
                await ctx.send("\n".join(Game(connect).getRank()))
            else:
                createImage()
                await ctx.send(file=discord.File('rank.png'))

    @ bot.command(name = 'start',help="'buyin amount' 'reserve' Default is 400,200")
    async def start(ctx, *args):
        if (ctx.channel.name == CHANNEL):
            game=Game(connect).newGame(*args)
            response=f"Started new game {game[0]} at {game[1]}"
            await ctx.send(response)
    
    @ bot.command(name = 'amount',help="'change buyin amount'")
    async def amount(ctx, *args):
        if (ctx.channel.name == CHANNEL):
            if len(args) > 0:
                response=Game(connect).changeBuy(args[0])
            else:
                response=f"Buyin amount has to be provided"
            await ctx.send(response)
    
    @ bot.command(name = 'reserve',help="'change reserve amount'")
    async def reserve(ctx, *args):
        if (ctx.channel.name == CHANNEL):
            if len(args) > 0:
                response=Game(connect).changereserve(args[0])
            else:
                response=f"reserve amount has to be provided"
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
