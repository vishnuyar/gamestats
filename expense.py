from connect import Connection
from datetime import datetime

class Expense:

    def __init__(self,conn):
        self.amount = 0
        self.description = None
        self.conn = conn
        if self.conn is None:
            raise Exception("DB Connection not available")

    def add(self,args):
        amount = args[0]
        self.description = " ".join(args[1:])
        try:
            self.amount = float(amount)
            if self.amount < 0:
                return "Expense amount cannot be negative"
            expenseTime = datetime.now()
            query = f"INSERT into expenses (amount,expense_time,description) VALUES({self.amount},'{expenseTime}','{self.description}')"
            result = self.conn.data_insert(query)
            if result:
                response = f"Expense details for {self.amount} added."
            else:
                response = f"Error while adding details for {self.amount}"
            return response
        except Exception as e:
            print(e)
            return "Expense amount has to be numeric"

    def showList(self,args):
        items = 5
        response = "\n"
        if len(args) > 0:
            try:
                items = int(args[0])
            except Exception as e:
                return "No of items has to be numeric"
        query = f"select * from expenses order by expense_time desc LIMIT {items}"
        result = self.conn.data_operations(query)
        for r in result:
            exp_date = str(r[2]).split(" ")[0]
            response +=f"{exp_date}-> {r[1]} :: {r[3]}\n"
        return response

    def balance(self):
        reserveTotal = 0.0
        expensesTotal = 0.0
        query = "select sum(reserve) from game"
        result = self.conn.data_operations(query)
        if result:
            reserveTotal = float(result[0][0])
        query = "select sum(amount) from expenses"
        result = self.conn.data_operations(query)
        if result:
            expensesTotal = float(result[0][0])
        balance = reserveTotal - expensesTotal
        return f"Reserve funds balance is: {balance}"