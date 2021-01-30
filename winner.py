from game import Game
from player import Player
from datetime import datetime
from ledger import Ledger

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
            totalAmount = sum(buyins.values())*amount - reserve
            winneramount = round(( totalAmount )*.667,-2)
            runneramount = totalAmount - winneramount
            if (winner.lower() in buyins.keys())  and (runner.lower() in buyins.keys()):
                return (winneramount,runneramount,amount,buyins,totalAmount,game_id)
            else:
                response = "The winners are not in the game played."
        else:
            response = "No game in progress"
        return response
    
    def getDivision(self,winners,profits,buyins,amount,game_id):
        division = {}
        amountbuyins = {}
        for player in buyins:
            if player not in winners:
                amountbuyins[player] = buyins[player]*amount

        
        #Assign reserve to the Treasurer
        if sum(amountbuyins.values()) > sum(profits):
            #Hard coding for Chandra for now -- later get it from treasurer name
            if ('chandra' in amountbuyins.keys()):
                reserveAmount = sum(amountbuyins.values()) - sum(profits)
                amountbuyins['chandra'] -= reserveAmount
                division['Reserve'] = f"Chandra->{reserveAmount}\n"
        for i in range(len(winners)):
            player = winners[i]
            amount = profits[i]
            division[player] = ""
            while (amount > 0) and (len(amountbuyins) > 0):
                names = list(amountbuyins.keys())
                playername = random.choice(names)
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
            division['Reserve'] = f"{playername.title()}->{amountbuyins[playername]}\n"
        return division
    
    def normalWin(self,winner,runner):
        result = self.prepareWin(winner,runner)
        if type(result) == tuple:
            winneramount,runneramount,amount,buyins,totalAmount,game_id = result
            winner_profit = winneramount - buyins[winner.lower()]*amount
            runner_profit = runneramount - buyins[runner.lower()]*amount
            winner_share = winneramount/totalAmount
            runner_share = runneramount/totalAmount
            response = self.addWins([winner.lower(),runner.lower()],[winner_profit,runner_profit],[winner_share,runner_share],buyins,amount,game_id)
            return response
        else:
            return result
        
    def addWins(self,winners,profits,shares,buyins,amount,game_id):
        response = ""
        for i in range(len(winners)):
            winner = winners[i]
            profit = profits[i]
            share = shares[i]
            self.addPlayerWin(winner.lower(),profit,share,buyins[winner.lower()]*amount,game_id)
            response += f"{winner.title()} : Gross {buyins[winner.lower()]*amount+profit} & Net :{profit}\n"
        response +="\n"
        result = Ledger(self.conn).createEntries(winners,profits,buyins,amount,game_id)
        if not result:
            #Close the game before sending response
            Game(self.conn).close()
            return response
        else:
            return "Failed to add entries to Ledger, game not closed"
    
    def ICMWin(self,chips1,chips2,winnername,runnername):
        chips =  [chips1,chips2]
        winners = [winnername,runnername]
        result = self.prepareWin(winners[0].lower(),winners[1].lower())
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
