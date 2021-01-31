
from game import Game

class Register:
    def __init__(self,conn):
        self.conn = conn
        if self.conn is None:
            raise Exception("DB Connection not available")
    
    def addPlayer(self,name):
        players=Game(self.conn).getPlayers()
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
