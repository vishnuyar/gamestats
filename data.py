class Details:

    def __init__(self):
        self.DISCORD_TOKEN=None
        self.DISCORD_GUILD =None
        self.DBUSER=None
        self.DBNAME=None
        self.DBPASSWORD=None
        self.readFile()
        

    def readFile(self):
        with open("database.ini") as dfile:
            lines = dfile.readlines()
        for line in lines:
            if line.startswith("DISCORD_TOKEN"):
                self.DISCORD_TOKEN = line.replace("DISCORD_TOKEN=","").replace("\n","")
            if line.startswith("GUILD"):
                self.DISCORD_GUILD = line.replace("GUILD=","").replace("\n","")
            if line.startswith("DBUSER"):
                self.DBUSER = line.replace("DBUSER=","").replace("\n","")
            if line.startswith("DBNAME"):
                self.DBNAME = line.replace("DBNAME=","").replace("\n","")
            if line.startswith("DBPASSWORD"):
                self.DBPASSWORD = line.replace("DBPASSWORD=","").replace("\n","")




if __name__ == '__main__':
    print(Details().DBUSER)