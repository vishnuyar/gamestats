# bot.py
from os import getenv
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands
from game import Game
from register import Register
from player import Player
from winner import Winner
from expense import Expense
from ledger import Ledger
from connect import Connection
from data import Details
from image import createImage
from graph import getChart
from analyze import Analyze


try:
    load_dotenv()
    # TOKEN=getenv('DISCORD_TOKEN')
    # GUILD=getenv('DISCORD_GUILD')
    TOKEN=Details().DISCORD_TOKEN
    GUILD=Details().DISCORD_GUILD
    
    CHANNEL=Details().CHANNEL
    connect=Connection()
    connect.connect()

    bot=commands.Bot(command_prefix = '',case_insensitive=True)

    @ bot.command(name = 'buy',help="'playername':Add as many players names as buyins")
    async def buy(ctx, *args):
        if (ctx.channel.name == CHANNEL):
            if len(args) > 0:
                game=Game(connect)
                response=game.addBuyins(args)
            else:
                response="Add player names for buyins"
            await ctx.send(response)

    @ bot.command(name = 'winner',help="'winnername' 'runnername': Add game winners")
    async def winner(ctx,*args):
        if (ctx.channel.name == CHANNEL):
            if (len(args) ==2):
                response=Winner(connect).normalWin(args[0],args[1])
            else:
                response = "You need two winners"
            await ctx.send(response)

    @ bot.command(name = 'icm',help="'highchips lowchips' 'winner runner':ICM win")
    async def icm(ctx,*args):
        if (ctx.channel.name == CHANNEL):
            if (len(args) == 4):
                response=Winner(connect).ICMWin(args[0],args[1],args[2],args[3])
            else:
                response = "You need to provide both chip counts and winners with space in between"
            await ctx.send(response)


    @ bot.command(name = 'game',help=" Current status of the game")
    async def game(ctx):
        if (ctx.channel.name == CHANNEL):
            response = Game(connect).getStatus()
            await ctx.send(response)
    
    @ bot.command(name = 'settle',help="'GameNo'/'all': Settles the ledger by option")
    async def settle(ctx,*args):
        if (ctx.channel.name == CHANNEL):
            if len(args) > 0:
                if args[0] == 'all':
                    args = []
                    response = Ledger(connect).clearLedger(args)
                else:
                    response = Ledger(connect).clearLedger(args)
            else:
                response = "Either GameNo. or all should be given"
            await ctx.send(response)

    @ bot.command(name = 'list',help="'no of items':List of expenditures, default 5")
    async def showexpenselist(ctx,*args):
        if (ctx.channel.name == CHANNEL):
            response = Expense(connect).showList(args)
            await ctx.send(response)

    @ bot.command(name = 'show',help=" Shows ledger balances")
    async def show(ctx):
        if (ctx.channel.name == CHANNEL):
            response = Ledger(connect).show()
            await ctx.send(response)

    @ bot.command(name = 'expense',help="'amount' 'description':Add expense details")
    async def game(ctx,*args):
        if (ctx.channel.name == CHANNEL):
            if len(args) > 1:
                response = Expense(connect).add(args)
            else:
                response = "Both Amount and description required for adding expense"
            await ctx.send(response)
    
    @ bot.command(name = 'balance',help=" Gives reserve fund balance")
    async def balance(ctx,*args):
        if (ctx.channel.name == CHANNEL):
            response = Expense(connect).balance()
            await ctx.send(response)

    @ bot.command(name = 'deletebuy',help="'playername': Removes player buyin")
    async def delbuy(ctx,*arg):
        if (ctx.channel.name == CHANNEL):
            if len(arg) > 0:
                response = Game(connect).delBuyin(arg[0])
            else:
                response = "Player name is compulsory to remove the buyin"
            await ctx.send(response)
    
    @ bot.command(name = 'rank',help="'lastNgames':  Leaderboard for the games")
    async def rank(ctx,*arg):
        if (ctx.channel.name == CHANNEL):
            createImage(arg)
            await ctx.send(file=discord.File('rank.png'))

    @ bot.command(name = 'analyze',help="'name':  Analyze this player")
    async def rank(ctx,*arg):
        if (ctx.channel.name == CHANNEL):
            if arg:
                Analyze(connect).analyze(lower(arg[0]))
                await ctx.send(file=discord.File('analyze.png'))
            else:
                await ctx.send("Need a player name to analyze")
    
    @ bot.command(name = 'chart',help="'lastNgames':'Rise of the players")
    async def rank(ctx,*arg):
        if (ctx.channel.name == CHANNEL):
            if arg:
                getChart(arg[0])
            else:
                getChart()
            await ctx.send(file=discord.File('chart.png'))

    @ bot.command(name = 'start',help="'buyin amount' 'reserve': Default is 400,200")
    async def start(ctx, *args):
        if (ctx.channel.name == CHANNEL):
            response=Game(connect).newGame(*args)
            await ctx.send(response)
    
    @ bot.command(name = 'amount',help="'buyin amount':Change Buyin Amount")
    async def amount(ctx, *args):
        if (ctx.channel.name == CHANNEL):
            if len(args) > 0:
                response=Game(connect).changeBuy(args[0])
            else:
                response=f"Buyin amount has to be provided"
            await ctx.send(response)
    
    @ bot.command(name = 'reserve',help="'amount':Change reserve amount'")
    async def reserve(ctx, *args):
        if (ctx.channel.name == CHANNEL):
            if len(args) > 0:
                response=Game(connect).changereserve(args[0])
            else:
                response=f"reserve amount has to be provided"
            await ctx.send(response)

    @ bot.command(name = 'register',help="'playername': Register a new player")
    async def register(ctx, arg):
        if (ctx.channel.name == CHANNEL):
            if arg:
                response = Register(connect).addPlayer(arg)
            else:
                response = "Please provide player name to register"
            await ctx.send(response)

    bot.run(TOKEN)
except Exception as e:
    print(e)
finally:
    connect.close()
