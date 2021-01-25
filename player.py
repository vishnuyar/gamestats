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

    def getPlayerName(self,id):
        query = f"select name from player where id = '{id}'"
        result = self.conn.data_operations(query)
        if result:
            return result[0][0]
        else:
            return None

    def isGamePlayer(player_id,game_id):
        query = "select count(player_id from buy where"

    

    