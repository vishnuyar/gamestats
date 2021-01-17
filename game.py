from connect import Connection
from datetime import datetime
# from numpy import genfromtxt
import text_to_image
import csv

class Game:
    def __init__(self,conn):
        self.conn = conn
        self.players = []
        if self.conn is None:
            raise Exception("DB Connection not available")
    def newGame(self,*args):
        buyinAmount = 400
        rent = 200
        gametime = datetime.now()
        if (len(args)>0):
            buyinAmount = args[0]
        if (len(args)>1):
            rent = args[1]
        query = f"INSERT INTO game (BUY_IN, RENT, START_TIME ) VALUES({buyinAmount},{rent},'{gametime}')"
        result = self.conn.data_insert(query)
        if result:
            query = "SELECT ID,START_TIME FROM game where ID = (SELECT MAX(ID) FROM game)"
            result = (self.conn.data_operations(query))
            for value in result:
                gameNo = value[0]
                gameTime = value[1]
        return gameNo,gameTime
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
        query = f"select name,count(player_id) from buy,player where game_id = {game_id} and buy.player_id = player.id group by game_id, player_id;"
        result = (self.conn.data_operations(query))
        for value in result:
            buyins[value[0]] = value[1]
        return buyins

    def getRent(self,game_id):
        rent = 0
        query = f"select rent from game where id = {game_id}"
        result = (self.conn.data_operations(query))
        for value in result:
            rent = value[0]
        return rent

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
                    status = Player(self.conn).addBuy(player,game_id)
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
        line = "----------------------------------------------"
        result_cols = ["Player    ","Games","Buyins","First","Second ","Net    "]
        # print(f"{','.join(result_cols)}")
        # print(line)
        response.append(f"{' '.join(result_cols)}")
        
        response.append(line)
    #r.append(result_cols)
        for row in result:
            if row[3]:
                name = row[1]
                games = row[2]
                buyins = row[3]
                if row[4]:
                    first = row[4]
                else:
                    first = 0
                if row[5]:
                    second = row[5]
                else:
                    second = 0
                if row[9]:
                    net = "{:4.1f}".format(row[9])
                else:
                    net = 0
                nextcol = name.ljust(10,' ').title()+str(games).rjust(5,' '),str(buyins).rjust(6,' '),str(first).rjust(5,' '),str(second).rjust(6,' '),(net).ljust(5,' ')
                # print((",".join(nextcol)))
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
        query = "select * from leaderboard order by first desc, second desc"
        result = (self.conn.data_operations(query))
        return result

        


class Player:
    def __init__(self,conn):
        self.conn = conn
        if self.conn is None:
            raise Exception("DB Connection not available")
    
    def addBuy(self,name,gamdeId):
        player_id = self.getPlayerId(name)
        if player_id:
            query = f"INSERT INTO buy (game_id,player_id) VALUES({gamdeId},{player_id})"
            result = self.conn.data_insert(query)
            return result
        else:
            return False

    def getPlayerId(self,name):
        query = f"select id from player where name = '{name}'"
        result = self.conn.data_operations(query)
        if result:
            return result[0][0]
        else:
            return None

    def isGamePlayer(player_id,game_id):
        query = "select count(player_id from buy where"

    

    


class Winner:
    def __init__(self,conn):
        self.conn = conn
        if self.conn is None:
            raise Exception("DB Connection not available")

    def addPlayerWin(self,player,profit,share,value,game_id):
        player_id = Player(self.conn).getPlayerId(player.lower())
        end_time = datetime.now()
        query = f"INSERT INTO winner (profit,share,value,game_id,player_id) VALUES({profit},{share},{value},{game_id},{player_id})"
        result = self.conn.data_insert(query)
        return result
    
    def normalWin(self,winner,runner):
        game = Game(self.conn)
        game_id = game.getGameId()
        if game_id:
            buyins = game.getBuyins(game_id)
            rent = game.getRent(game_id)
            amount = game.getBuyAmount(game_id)
            totalAmount = sum(buyins.values())*amount
            winneramount = round(( totalAmount - rent)*.667,-2)
            runneramount = totalAmount - rent - winneramount
            if (winner.lower() in buyins.keys())  and (runner.lower() in buyins.keys()):
                winner_profit = winneramount - buyins[winner.lower()]*amount
                runner_profit = runneramount - buyins[runner.lower()]*amount
                winner_share = winneramount/totalAmount
                runner_share = runneramount/totalAmount
                self.addPlayerWin(winner,winner_profit,winner_share,buyins[winner.lower()]*amount,game_id)
                self.addPlayerWin(runner,runner_profit,runner_share,buyins[runner.lower()]*amount,game_id)
                game.close()
                response = f"{winner.title()} : {winneramount}, {runner.title()} : {runneramount}"
            else:
                response = "The winners are not in the game played."
        else:
            response = "No game in progress"
        return response

    def ICMWin(self):
        pass

class Register:
    def __init__(self,conn):
        self.conn = conn
        if self.conn is None:
            raise Exception("DB Connection not available")
    def addPlayer(self,name):
        query = f"INSERT INTO player (NAME ) VALUES('{name}')"
        result = self.conn.data_insert(query)
        if result:
            query = f"SELECT name FROM player where name = '{name}'"
            result = (self.conn.data_operations(query))
            for value in result:
                name = value[0]
                return name


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
