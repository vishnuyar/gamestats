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
        buyinAmount = 400
        reserve = 200
        rent = 0
        gametime = datetime.now()
        if (len(args)>0):
            buyinAmount = args[0]
        if (len(args)>1):
            reserve = args[1]
        query = f"INSERT INTO game (BUY_IN, RENT, START_TIME,RESERVE ) VALUES({buyinAmount},{rent},'{gametime}',{reserve})"
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
    
    def prepareWin(self,winner,runner):
        game = Game(self.conn)
        game_id = game.getGameId()
        if game_id:
            buyins = game.getBuyins(game_id)
            reserve = float(game.getreserve(game_id))
            amount = float(game.getBuyAmount(game_id))
            totalAmount = sum(buyins.values())*amount
            winneramount = round(( totalAmount - reserve)*.667,-2)
            runneramount = totalAmount - reserve - winneramount
            if (winner.lower() in buyins.keys())  and (runner.lower() in buyins.keys()):
                return (winneramount,runneramount,amount,buyins,totalAmount,game_id)
            else:
                response = "The winners are not in the game played."
        else:
            response = "No game in progress"
        return response
    
    def getDivision(self,winners,profits,buyins,amount):
        division = {}
        amountbuyins = {}
        for player in buyins:
            if player not in winners:
                amountbuyins[player] = buyins[player]*amount
        for i in range(len(winners)):
            player = winners[i]
            amount = profits[i]
            division[player] = ""
            while (amount > 0) and (len(amountbuyins) > 0):
                names = list(amountbuyins.keys())
                playername = names[0]
                if amountbuyins[playername] > amount:
                    sendamount = amount
                    amountbuyins[playername] -= sendamount
                    amount = 0
                else:
                    sendamount = amountbuyins[playername]
                    amount -= sendamount
                    amountbuyins.pop(playername)
                division[player] += (f"{playername.title()}->{sendamount}\n")
        if len(amountbuyins) > 0:
            division['Reserver'] = f"{playername.title()}->{amountbuyins[playername]}\n"
        return division
    
    def normalWin(self,winner,runner):
        result = self.prepareWin(winner,runner)
        if type(result) == tuple:
            winneramount,runneramount,amount,buyins,totalAmount,game_id = result
            winner_profit = winneramount - buyins[winner.lower()]*amount
            runner_profit = runneramount - buyins[runner.lower()]*amount
            winner_share = winneramount/totalAmount
            runner_share = runneramount/totalAmount
            response = self.addWins([winner,runner],[winner_profit,runner_profit],[winner_share,runner_share],buyins,amount,game_id)
            return response
        else:
            return result
        
    def addWins(self,winners,profits,shares,buyins,amount,game_id):
        response = ""
        for i in range(len(winners)):
            winner = winners[i]
            profit = profits[i]
            share = shares[i]
            self.addPlayerWin(winner,profit,share,buyins[winner.lower()]*amount,game_id)
            response += f"{winner.title()} : Gross {buyins[winner.lower()]*amount+profit} & Net :{profit}\n"
        response +="\n"
        divmesg = self.getDivision(winners,profits,buyins,amount)
        for player in divmesg:
            response += f"To {player.title()} :\n{divmesg[player]}\n"
        #Close the game before sending response
        Game(self.conn).close()
        return response
    
    def ICMWin(self,chipsCount,winnerName):
        chips = chipsCount.split('/')
        winners = winnerName.split('/')
        result = self.prepareWin(winners[0],winners[1])
        if type(result) == tuple :
            try:
                winnerChips = int(chips[0]) 
                runnerChips = int(chips[1])
                chipsTotal = winnerChips + runnerChips
                winneramount,runneramount,amount,buyins,totalAmount,game_id = result
                winDiff = winneramount - runneramount
                firstWinner = round((winDiff*(winnerChips/chipsTotal) + runneramount),-2)
                secondWinner = winneramount + runneramount - firstWinner
                winner_profit = firstWinner - buyins[winners[0].lower()]*amount
                runner_profit = secondWinner - buyins[winners[1].lower()]*amount
                winner_share = firstWinner/totalAmount
                runner_share = secondWinner/totalAmount
                if winner_share == runner_share:
                    winner_share = 0.501
                    runner_share = 0.499
                response = self.addWins(winners,[winner_profit,runner_profit],[winner_share,runner_share],buyins,amount,game_id)
                return response
            except Exception as e:
                print(e)
                return "Chips should be in Numbers"
        else:
            return result

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
