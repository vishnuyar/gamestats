class Player:
    def __init__(self,conn):
        self.conn = conn
        if self.conn is None:
            raise Exception("DB Connection not available")

    def getPlayers(self):
        players = {}
        query = "select distinct(name),id from player"
        result = (self.conn.data_operations(query))
        for value in result:
            players.update({value[0]:value[1]})
        return players

    def addPlayer(self,name):
        players=self.getPlayers()
        name=name.lower()
        if name in players:
            return f"{name.title()} is already a registered player"
        else:
            query = f"INSERT INTO player (NAME ) VALUES('{name}')"
            result = self.conn.data_insert(query)
            if result:
                return f"you have registered player {name.title()}"
            else:
                return f"Error encountered when trying to register {name.title()}"

    def getPlayerId(self,name):
        query = f"select id from player where name = '{name}'"
        result = self.conn.data_operations(query)
        if result:
            return result[0][0]
        else:
            return None

    def getPlayerName(self,id):
        query = f"select name from player where id = '{id}'"
        result = self.conn.data_operations(query)
        if result:
            return result[0][0]
        else:
            return None

    def getPlayerDict(self):
        playerDict = {}
        query = "select id,name from player"
        result = self.conn.data_operations(query)
        for r in result:
            playerDict.update({r[0]:r[1]})
        return playerDict


    
