
from connect import Connection
from datetime import datetime
from player import Player
import random

class Ledger:
    def __init__(self,conn):
        self.conn = conn
        if self.conn is None:
            raise Exception("DB Connection not available")

    def createEntries(self,winners,profits,buyins,amount,game_id):
        division = {}
        amountbuyins = {}
        for player in buyins:
            if player not in winners:
                amountbuyins[player] = buyins[player]*amount
        #Add winner details to Ledger
        ledger = Ledger(self.conn)
        for i in range(len(winners)):
            player = winners[i]
            amount = profits[i]
            result  = self.addtoLedger(player,amount,game_id)
            if not result:
                print("Error adding to ledger details of winners")
                return False
        #Add other players detail to Ledger
        for player in amountbuyins:
            result  = self.addtoLedger(player,amountbuyins[player]*(-1),game_id)
            if not result:
                print("Error adding to ledger details of players")
                return False
    
    
    def addtoLedger(self,name,amount,game_id):
        ledger_time = datetime.now()
        player_id = Player(self.conn).getPlayerId(name)
        if player_id:
            query = f"INSERT INTO ledger (amount,ledger_time,game_id,player_id) VALUES ({amount},'{ledger_time}',{game_id},{player_id})"
            result = self.conn.data_insert(query)
            return True
        else:
            return False

    def clearLedger(self,args):
        game_id = None
        if len(args) > 0:
            try:
                game_id = int(args[0])
                if (self.isGameId(game_id)):
                    if not self.isSettled(game_id):
                        details = self.getDetails(game_id)
                        singleGame = True
                    else:
                        return "This game has already been settled."
                else:
                    return "This game does not exist"
            except Exception as e:
                print(e)
                return "Game id has to be numeric"
        else:
            details = self.getDetails()
        if type(details) == dict:
            result = self.closeLedger(game_id)
            if result:
                response = "\n"
                recd = self.prepareResponse(details)
                for player in recd:
                    response += f"To {player.title()} :\n{recd[player]}\n"
                return response
            else:
                return "Error settling games and clearing Ledger"
        else:
            return details         
         
    def closeLedger(self,game_id=None):
        if game_id:
            query = f"select distinct(game_id) from ledger where game_id={game_id}" 
            delquery = f"delete from ledger where game_id={game_id}"
        else:
            query = "select distinct(game_id) from ledger"
            delquery = "delete from ledger"
        result = (self.conn.data_operations(query))
        for r in result:
            game_id = int(r[0])
            query = f"update game set settled = 1 where id = {game_id}"
            result = self.conn.data_insert(query)
            if not result:
                return False
        # Deleting settled games from the ledger
        result = self.conn.data_insert(delquery)
        if result:
            return True
        else:
            print("Error while deleting details in ledger")
            return False

    def show(self):
        details = self.getDetails()
        if type(details) == dict:
            if len(details) > 0:
                response = "\n"
                positive = "\n"
                negative = "\n"
                reserveAmount = sum(details.values())*-1
                for playername in details:
                    if details[playername] > 0:
                        positive +=f"{playername.title()} <- {details[playername]}\n"
                    else:
                        negative +=f"{playername.title()} -> {details[playername]*-1}\n"
                response = "Receive:"+positive
                if reserveAmount > 0:
                    response +=f"Reserve <-{reserveAmount}\n"
                response +="\nSend:"+negative
                return response
            else:
                return "Nothing to show. All settled."
        else:
            return details
    
    def isSettled(self,game_id):
        query = f"select settled from game where id = {game_id}"
        result = self.conn.data_operations(query)
        settled = int(result[0][0])
        if settled:
            return True
        else:
            return False
    
    def isGameId(self,game_id):
        query = f"select id from game where id = {game_id}"
        result = self.conn.data_operations(query)
        if result:
            givenid = int(result[0][0])
            if givenid == game_id:
                return True
            else:
                return False



    def getDetails(self,game_id=None):
        if game_id:
            query = f"select player_id,sum(amount) from ledger where game_id={game_id} group by player_id "
        else:
            query = "select player_id,sum(amount) from ledger group by player_id"
        result = (self.conn.data_operations(query))
        details = {}
        for r in result:
            player_id = r[0]
            name = Player(self.conn).getPlayerName(player_id)
            amount = r[1]
            if name:
                details[name] = amount
            else:
                return("Error getting player name, ledger clearing stopped")
        return details
    
    def prepareResponse(self,details):
        positive = {}
        negative = {}
        division = {}
        for player in details:
            if details[player] > 0:
                positive[player] = details[player]
            else:
                negative[player] = details[player]*-1
        if sum(negative.values()) > sum(positive.values()):
            #Hard coding for Chandra for now -- later get it from treasurer name
            if ('chandra' in negative.keys()):
                reserveAmount = sum(negative.values()) - sum(positive.values())
                negative['chandra'] -= reserveAmount
                division['Reserve'] = f"Chandra->{reserveAmount}\n"
        for player in positive:
            amount = positive[player]
            division[player] = ""
            while (amount > 0) and (len(negative) > 0):
                names = list(negative.keys())
                playername = random.choice(names)
                if negative[playername] > amount:
                    sendamount = amount
                    negative[playername] -= sendamount
                    amount = 0
                else:
                    sendamount = negative[playername]
                    amount -= sendamount
                    negative.pop(playername)
                division[player] += (f"{playername.title()}->{sendamount}\n")
        print(f"negative left:{negative}")
        if len(negative) > 0:
            division['Reserve'] = f"{playername.title()}->{negative[playername]}\n"
        return division
