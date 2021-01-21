#import mysql.connector
#from mysql.connector import Error
import psycopg2
from dotenv import load_dotenv
from data import Details

class Connection:

    def __init__(self):
        self.conn = None
        load_dotenv()
        # self.user=os.getenv('DBUSER')
        # self.password=os.getenv('DBPASSWORD')
        # self.dbname=os.getenv('DBNAME')
        self.user=Details().DBUSER
        self.password=Details().DBPASSWORD
        self.dbname=Details().DBNAME
        self.dbpasswd=Details().DBPASSWORD


    def data_insert(self,query):
        """ Function which performs database operations and returns results """
        try:
            #creating a cursor for connection
            if self.conn:
                cursor = self.conn.cursor()
                #executing the query on the database and get the results
                # print(f"query:{query}")
                cursor.execute(query)
                #If No error is enountered, cursor is closed
                cursor.close()
                #Committing the data operatios
                self.conn.commit()
                #On successful completion return the results
                return True
            else:
                print("Database connection not establised")
                return False
        except Exception as e:
            print(e)
            return False
        
        

    def data_operations(self,query):
        """ Function which performs database operations and returns results """
        try:
            #creating a cursor for connection
            if self.conn:
                cursor = self.conn.cursor()
                #executing the query on the database and get the results
                # print(f"query:{query}")
                cursor.execute(query)
                results = cursor.fetchall()
            else:
                print("Database connection not establised")
        except Exception as e:
            print(e)
            return "error in data operations"
        
        #If No error is enountered, cursor is closed
        cursor.close()
        #Committing the data operatios
        self.conn.commit()
        #On successful completion return the results
        return results

    def connect(self):
        """ Connect to MySQL database """
        try:
            self.conn = psycopg2.connect(host='localhost',
                                        database=self.dbname,
                                        user=self.user,
                                        password=self.dbpasswd)
            if self.conn:
                print('Connected to PostgreSQL database')

        except Exception as e:
            print(e)

    def close(self):
        if self.conn is not None:
            self.conn.close()
            print("Database connection closed")


if __name__ == '__main__':
    c = Connection()
    c.connect()
    query = "select name from player"
    print(c.data_operations(query))
    c.close()