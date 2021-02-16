import psycopg2
import pandas as pd
from sqlalchemy import create_engine
from data import Details
import matplotlib.pyplot as plt


def getChart(no_of_games=None):
    # Create an engine instance
    # dialect+driver://username:password@host:port/database
    try:
        no_of_games = int(no_of_games)
    except Exception as e:
        print(e)
        no_of_games = None

    dt = Details()
    alchemyEngine   = create_engine(f"postgresql+psycopg2://{dt.DBUSER}:{dt.DBPASSWORD}@127.0.0.1/{dt.DBNAME}")
    # Connect to PostgreSQL server

    dbConnection    = alchemyEngine.connect()

    sql_query = pd.read_sql_query("select * from games_played_2021 order by game_id",dbConnection)

    df = pd.DataFrame(sql_query, columns=['game_id','vishnu','ramesh','kisor','rajesh','chandra','sudhir'])
    newdf = df.groupby('game_id').sum()
    if no_of_games:
        newdf = newdf[no_of_games*-1:]
    print(newdf[-80:])
    # print (newdf.tail())
    for col in newdf.columns:
        if col != 'game_id':
            newdf[col] = newdf[col].cumsum()
        
    # print(newdf.tail())

    fig = plt.figure(figsize=(10,8),clear=True)
    plt.style.use('fivethirtyeight')
    ax = fig.add_subplot(1,1,1)
    colors = ['sienna','darkgoldenrod','crimson','forestgreen','dodgerblue','indigo']
    for i,col in enumerate(newdf.columns):
        newdf[col].plot(y=col,color = colors[i],ax=ax,legend=True)
        
    left,right = ax.get_xlim()
    bottom, top = ax.get_ylim()
    # print(left,right,bottom,top)
    ax.set_facecolor('lightgrey')
    ax.text(left,top,"Who is reaching for the top?",weight='bold',size=18,alpha=0.7)
    ax.text(right,bottom-1.5,s="Made by Vishnu",ha='right',va='bottom',size=9,weight='bold',color='w',backgroundcolor='black',alpha=0.7)
    ax.set_xlabel("")
    fig.show()
    fig.savefig("chart.png")

if __name__ == "__main__":
    getChart()