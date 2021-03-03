import pandas as pd 

class ReadLog:
    PLAYER_JOINED = "The admin approved the player"
    PLAYER_QUITS = "quits the game with a stack of"

    def __init__(self,filename):
        self.logLines = None
        self.playerId = None
        self.filename = filename
        self.messages = []
        self.name = None
        self.winners = None
        self.buyins = None
        self.fileRead()

    def fileRead(self):
        rl = []
        with open(self.filename) as f:
            for line in f:
                rl.append(line)
        print(f"Read {len(rl)} of log for the game")
        self.logLines = rl
        self.getPlayers()

    def getPlayers(self):
        players ={}
        winners = {}
        last_player = None
        for i in range(len(self.logLines) -1,0,-1):
            line = self.logLines[i]
            if self.PLAYER_JOINED in line:
                message = line.split(",")[0]
                player_longId = message.split('""')[1]
                player = player_longId.split("@")[0].replace(' ','').lower()
                if player in players:
                    players[player] +=1
                else:
                    players[player]  = 1
            if self.PLAYER_QUITS in line:
                message = line.split(",")[0]
                player_longId = message.split('""')[1]
                stack = (message.split('""')[2].replace(self.PLAYER_QUITS,'').replace(' ','').replace('.','').replace('"',""))
                quitplayer = player_longId.split("@")[0].replace(' ','').lower()
                try:
                    chips = int(stack)
                except Exception as e:
                    print(f"The error while converting to int of stack {e}")
                    chips = 0
                if chips > 0:
                    winners[quitplayer] = chips
                else:
                    # print(f"replacing {last_player} with {quitplayer}")
                    last_player = quitplayer
                
                # print(f"The quit player is {player} and his stack is {chips}")
        if len(winners) == 1:
            winners[last_player] = 0
        self.buyins = players
        self.winners = winners
        # print(f"the player buyins is {players}")
        # print(f"The winners and stack are {winners}")
        # print(f"The last player to quit is {last_player}")
    def pandaRead(self):
        log_df = pd.read_csv(self.filename)
        print(f"The log df details are {log_df.shape}")
        for col in log_df:
            print(f"the columns is {col}")
            print(log_df[col].value_counts())



if __name__ == "__main__":
    filename = "poker_now_log_VYVPiCvr1HbFqBvlBcG3mIeSU.csv"
    filename = "poker_now_log_a7afsO3ESyr_1_FEgRQixY5PS.csv"
    l = ReadLog(filename)
    print(l.winners)
    print(l.buyins)