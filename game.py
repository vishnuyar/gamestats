from connect import Connection
from datetime import datetime
from ledger import Ledger
from player import Player
import random
# from numpy import genfromtxt
import text_to_image
import csv

class Game:
    def __init__(self,conn):
        self.conn = conn
        self.players = []
        if self.conn is None:
            raise Exception("DB Connection not available")
    
    def getBuyinId(self,player_id,game_id):
        query = f"select max(id) from buy where player_id = {player_id} and game_id = {game_id}"
        result = self.conn.data_operations(query)
        if result:
            return result[0][0]
        else:
            return None

    def delBuyin(self,playername):
        game_id = self.getGameId()
        if game_id:
            player_id = Player(self.conn).getPlayerId(playername.lower())
            if player_id:
                buyin_id = self.getBuyinId(player_id,game_id)
                if buyin_id:
                    query = f"delete from buy where id = {buyin_id}"
                    result = self.conn.data_insert(query)
                    if result:
                        return f"one Buyin removed for {playername}"
                    else:
                        return f"Failed to remove Buyin for {playername}"
                else:
                    return f"{playername} does not have buyin in Game:{game_id}" 
            else:
                return f"{playername.title()} is not a registered player" 
        else:
            return "No game in progress to remove buyin"

    def changeBuy(self,newBuyin):
        try:
            amount = float(newBuyin)
            game_id = self.getGameId()
            if game_id:
                query = f"update game set buy_in ={amount} where id = {game_id}"
                result = self.conn.data_insert(query)
                if result:
                    return f"Buyin amount changed to {amount}"
                else:
                    return "Failed to change Buyin Amount"
            else:
                return "No Game in progress to change Buyin Amount"
        except Exception as e:
            print(e)
            return "The Buyin amount has to be a number"
    
    def changereserve(self,newReserve):
        try:
            amount = float(newReserve)
            game_id = self.getGameId()
            if game_id:
                query = f"update game set reserve ={amount} where id = {game_id}"
                result = self.conn.data_insert(query)
                if result:
                    return f"reserve amount changed to {amount}"
                else:
                    return "Failed to change reserve Amount"
            else:
                return "No Game in progress to change reserve Amount"
        except Exception as e:
            print(e)
            return "The reserve amount has to be a number"
    
    def newGame(self,*args):
        game_id = self.getGameId()
        if not game_id:
            buyinAmount = 400
            reserve = 200
            rent = 0
            settled = 0
            gametime = datetime.now()
            if (len(args)>0):
                buyinAmount = args[0]
            if (len(args)>1):
                reserve = args[1]
            query = f"INSERT INTO game (BUY_IN, RENT, START_TIME,RESERVE,SETTLED ) VALUES({buyinAmount},{rent},'{gametime}',{reserve},{settled})"
            result = self.conn.data_insert(query)
            if result:
                query = "SELECT ID,START_TIME FROM game where ID = (SELECT MAX(ID) FROM game)"
                result = (self.conn.data_operations(query))
                for value in result:
                    gameNo = value[0]
                    gameTime = value[1]
            return f"Started new game {gameNo} at {gameTime}"
        else:
            return f"Game {game_id} is already running."
    
    def getGameId(self):
        query = "select max(id) from game where end_time is null"
        result = self.conn.data_operations(query)
        if result:
            return result[0][0]
        else:
            return None
    
    def getPlayers(self):
        players = []
        query = "select distinct(name) from player"
        result = (self.conn.data_operations(query))
        for value in result:
            players.append(value[0])
        return players

    def getBuyins(self,game_id):
        buyins = {}
        players = {}
        query = f"select id,name from player"
        result = (self.conn.data_operations(query))
        for r in result:
            players[r[0]]=r[1]
        query = f"select player_id,count(player_id) from buy where game_id = {game_id}  group by game_id, player_id;"
        buyinsResult = (self.conn.data_operations(query))
        for value in buyinsResult:
            buyins[players[value[0]]] = value[1]
        return buyins

    def getreserve(self,game_id):
        reserve = 0
        query = f"select reserve from game where id = {game_id}"
        result = (self.conn.data_operations(query))
        for value in result:
            reserve = value[0]
        return reserve

    def getBuyAmount(self,game_id):
        amount = 0
        query = f"select buy_in from game where id = {game_id}"
        result = (self.conn.data_operations(query))
        for value in result:
            amount = value[0]
        return amount

    
    def getStatus(self):
        game_id = self.getGameId()
        if game_id:
            buyins = self.getBuyins(game_id)
            response = self.buyinResponse(buyins)
        else:
            response = "No game in progress"
        return response
    
    def buyinResponse(self,buyins):
        buyins_data = [f"{key.title()} : {buyins[key]} " for key in buyins]
        totalBuyins = sum(buyins.values())
        response = f"Buyins : {totalBuyins}\n{' '.join(buyins_data)}\n"
        return response
    
    def addBuyins(self,buys):
        nonplayers=[]
        buyins={}
        players = self.getPlayers()
        game_id = self.getGameId()
        if game_id:
            for player in buys:
                if player.lower() in players:
                    status = Player(self.conn).addBuy(player.lower(),game_id)
                    if status:
                        if player in buyins.keys():
                            buyins[player] += 1
                        else:
                            buyins[player] = 1
                else:
                    nonplayers.append(player)
            response = ""
            if len(buyins) > 0:
                response = self.buyinResponse(buyins)
            if len(nonplayers) > 0:
                response += f"\nThese players are not registered \n{'-'.join(nonplayers)}\n"
        else:
                response="No game in progress. Start a new Game"
        # print(response)
        return response
    
    def rankResponse(self,result):
        response = []
        line = "---------------------------------------------"
        result_cols = ["Player    ","Games","Buyins","First","Second","S/R    "]
        # print(f"{','.join(result_cols)}")
        # print(line)
        response.append(f"{' '.join(result_cols)}")
        
        response.append(line)
        #r.append(result_cols)
        for row in result:
            if row[2]:
                name = row[0]
                games = row[1]
                buyins = row[2]
                if row[3]:
                    first = int(row[3])
                else:
                    first = 0
                if row[4]:
                    second = int(row[4])
                else:
                    second = 0
                strikerate = "{:4.1f}".format((first+second)*100/games)
                if row[5]:
                    net = "{:4.1f}".format(row[5])
                else:
                    net = 0
                nextcol = name.ljust(10,' ').title()+str(games).rjust(5,' '),str(buyins).rjust(6,' '),str(first).rjust(5,' '),str(second).rjust(6,' '),(strikerate).rjust(5,' ')
                response.append(f"{' '.join(nextcol)}")
                # response.append(line)
        return response

    
    def getRank(self):
        leaderrank = self.getLeaderBoard()
        return self.rankResponse(leaderrank)
    
    def close(self):
        game_id = self.getGameId()
        end_time = datetime.now()
        query = f"update game set end_time = '{end_time}' where id = {game_id}"
        result = self.conn.data_insert(query)

    def getLeaderBoard(self):
        query = "select name,games_played,total_buyins,coalesce(first,0) as firstN,coalesce(second,0) as secondN,net_win,(first+second) as total from leaderboard where games_played > 0 order by total desc NULLS LAST,first desc NULLS LAST, second desc NULLS LAST, net_win desc"
        result = (self.conn.data_operations(query))
        return result

        








if __name__ == '__main__':
    c = Connection()
    c.connect()
    g = Game(c)
    result = g.getRank()
    st = "\n".join(result)
    encoded_image_path = text_to_image.encode(st, "image.png")
    encoded_image_path = text_to_image.encode("Hello World!", "what.png")
    print("\n".join(result))

    # with open("leader.csv","w") as csvfile:
    #     writer = csv.writer(csvfile)
    #     for r in result:
    #         writer.writerow(r)
