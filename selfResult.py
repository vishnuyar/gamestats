from readlog import ReadLog
from player import Player
from game import Game
from winner import Winner
from connect import Connection
import collections

class SelfResult:
    def __init__(self,conn):
        self.buyins = None
        self.winners = None
        self.conn = conn
        self.messages = []
        if self.conn is None:
            raise Exception("DB Connection not available")
        self.gameObj = Game(self.conn)
        self.gameId = self.gameObj.getGameId()


    def getResults(self,filename):
        if self.gameId:
            logRead = ReadLog(filename)
            self.buyins = logRead.buyins
            self.winners = logRead.winners
            try:
                self.registerPlayers()
                self.registerBuyins()
                #self.registerWin()

            except Exception as e:
                print(f"Error while processing result: {e} ")
        else:
            self.messages.append("First start the game. No game Running")

        return self.messages


    def registerPlayers(self):
        playerObj = Player(self.conn)
        players = playerObj.getPlayers()
        for player in self.buyins:
            if player not in players:
                #Register this player to the system
                self.messages.append(playerObj.addPlayer(player))
        #Since all players are entered, refresh the players
        self.playerIds = playerObj.getPlayers()

    def registerBuyins(self):
        buys = []
        for player in self.buyins:
            buyin_count = self.buyins[player]
            for i in range(buyin_count):
                buys.append(player)
        #Now add the buyins
        self.messages.append(self.gameObj.addBuyins(buys))

    def registerWin(self):
        
        if len(self.winners) == 2:
            self.winnerObj = Winner(self.conn)
            sorted_winners = {k: v for k, v in sorted(self.winners.items(), key=lambda item: item[1])}
            print(sorted_winners)
            winnerChips = list(sorted_winners.values())
            print(f"winnerchips {winnerChips}")
            winners = list(sorted_winners.keys())
            print(f"winner names {winners}")
            #Sorting is in ascending order, need to reverse the winners
            if 0 in winnerChips:
                self.messages.append(self.winnerObj.normalWin(winners[1],winners[0]))
            else:
                self.messages.append(self.winnerObj.ICMWin(winnerChips[1],winnerChips[0],winners[1],winners[0]))
        else:
            self.messages.append(f"Currently only two winners are accepted. We got {len(self.winners)}")
            
if __name__ == "__main__":
    filename = "poker_now_log_VYVPiCvr1HbFqBvlBcG3mIeSU.csv"
    filename = "poker_now_log_a7afsO3ESyr_1_FEgRQixY5PS.csv"
    conn = Connection()
    conn.connect()
    l = SelfResult(conn)
    print(l.getResults(filename))          

                


