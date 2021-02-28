from connect import Connection
from player import Player
from PIL import Image, ImageDraw, ImageFont
import os

class Analyze:
    def __init__(self,conn):
        self.playerId = None
        self.conn = conn
        self.messages = []
        self.name = None
        if self.conn is None:
            raise Exception("DB Connection not available")
    
    def analyze(self,name):
        self.name = name
        self.playerId = Player(self.conn).getPlayerId(name)
        # print(f"The player id of {name} is {self.playerId}")
        if self.playerId:
            self.gamebyYears()
            self.streaks()
        else:
            self.messages.append("********************")
            self.messages.append("This player does not exist")
            self.messages.append("********************")
        self.createImage()

    def gamebyYears(self):
        query = f"select count(id),EXTRACT(YEAR FROM start_time) from game where id in (select distinct(game_id) from buy where player_id = {self.playerId}) group by EXTRACT(YEAR FROM start_time)"
        result = self.conn.data_operations(query)
        yearresults = {}
        for r in result:
            yearresults.update({r[1]:[r[0]]})

    
        query = f"select count(id),EXTRACT(YEAR FROM start_time) from game where id in (select distinct(game_id) from winner where player_id = {self.playerId}) group by EXTRACT(YEAR FROM start_time)"
        result = self.conn.data_operations(query)
        for r in result:
            yearresults[r[1]].append(r[0])
        
        for year in yearresults:
            self.messages.append(f"Year {int(year)} played {yearresults[year][0]} and won {yearresults[year][1]} with S/R of {(yearresults[year][1]/yearresults[year][0])*100:.2f}")

    def streaks(self):
        play_query = f"select distinct(game_id) from buy where player_id = {self.playerId} order by game_id"
        win_query = f"select distinct(game_id) from winner where player_id = {self.playerId} order by game_id"
        play_list = []
        win_list = []
        result = self.conn.data_operations(play_query)
        for r in result:
            play_list.append(r[0])
        result = self.conn.data_operations(win_query)
        for r in result:
            win_list.append(r[0])
        self.messages.append("***************************")
        self.messages.append(f"Total played {len(play_list)} and won {len(win_list)} with S/R of {len(win_list)/len(play_list)*100:.2f}")
        self.messages.append("***************************")
        winStreak = 0
        loseStreak = 0
        maxWinStreak = 0
        maxLoseStreak = 0
        lMax = []
        wMax = []
        winStreaks = []
        loseStreaks = []
        for game in play_list:
            if game in win_list:
                winStreak += 1
                winStreaks.append(game)
                if loseStreak > maxLoseStreak:
                    maxLoseStreak = loseStreak
                    lMax = loseStreaks.copy()
                loseStreak = 0
                loseStreaks =[]
                
            else:
                loseStreak += 1
                loseStreaks.append(game)
                if winStreak > maxWinStreak:
                    maxWinStreak = winStreak
                    wMax = winStreaks.copy()
                winStreak = 0
                winStreaks = []

        

        # print(f"maxwinStreak is {maxWinStreak} and maxlosestreak is {maxLoseStreak}")
        # print(f"win streak is {wMax}")
        # print(f" lose streak is {lMax}")
        
        
        # print(f"avg buys in Longest lose streak is {loseBuys/len(lMax)}")
        # print(f"avg buys in Longest win streak is {winBuys/len(wMax)}")
        
        
        no_winList = list(set(play_list).difference(set(win_list)))
        # print(len(no_winList),len(play_list),len(win_list))
        
        if len(wMax)>0:
            winBuys = self.avgBuys(wMax)
            self.messages.append(f"The longest winning streak is {maxWinStreak} with Avg buys of {winBuys/len(wMax):.2f}")
        if len(lMax)>0:
            loseBuys = self.avgBuys(lMax)
            self.messages.append(f"The longest losing streak is {maxLoseStreak} with Avg buys of {loseBuys/len(lMax):.2f}")
        self.messages.append(" ")
        if winStreak > 0:
            self.messages.append(f"\nCurrently in Winning streak of {(winStreak)}, and games are {winStreaks}")
        if loseStreak > 0:
            self.messages.append(f"\nCurrently in Losing streak of {(loseStreak)},and games are {loseStreaks}")
        self.messages.append(" ")
        if len(win_list)>0:
            self.messages.append(f"Avg buys when winning {self.avgBuys(win_list)/len(win_list):.2f}")
        if len(no_winList)>0:
            self.messages.append(f"Avg buys when losing {self.avgBuys(no_winList)/len(no_winList):.2f}")
        self.messages.append(f"avg buys when Playing {self.avgBuys(play_list)/len(play_list):.2f}")



    def avgBuys(self,wMax):
        st = ','.join([str(elem) for elem in wMax])
        # print(f"st is {st}")
        query = f"select count(game_id) from buy where player_id = {self.playerId} and game_id in ({st })"
        result = self.conn.data_operations(query)
        for r in result:
            return r[0]

    def createImage(self):
        # name of the file to save
        filename = "analyze.png"
        fnt1 = ImageFont.truetype('Arial.ttf', 15)
        fnt = ImageFont.load_default()
        length = len(self.messages)*30
        # create new image
        image = Image.new(mode = "RGB", size = (525,length), color = "#EDF5E1")
        draw = ImageDraw.Draw(image)
        # #143D59,#F4B41A #EDF5E1 0B0C10 #EEE2DC #AC3B61 #25274D #29648A
        i = 10
        
        text = f"Analysis of {self.name}"
        draw.text((200,5), text=text, font=fnt1,align="middle", fill="#143D59")
        for message in self.messages:
            # print(r)
            i+=20
            draw.text((10,i), text=message, font=fnt, fill="#0B0C10")
            # i+=20
        image.save(filename)

if __name__ == "__main__":
    conn = Connection()
    conn.connect()
    a = Analyze(conn)
    t = a.analyze("kasap")
    
