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
