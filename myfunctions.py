import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from operator import itemgetter

from helpers import apology, login_required, lookup, usd

app = Flask(__name__)
app.jinja_env.filters["usd"] = usd
db = SQL("sqlite:///finance.db")




# get username for user
# input is user_id, output is the username
def user_name(user_id):
    user = user_id
    usernamex = db.execute("SELECT username FROM users WHERE id = :user_id", user_id = user)
    username = usernamex[0]["username"]
    return username

# gets the stock with prices, buy price etc for the user
# input is username
# output is a user_own, total_cash, overall_cash, profit, profitz
    # user_own = (list of list of stocks that user owns. each individual list includes name, symbol, avgbuy price, current price, total price in that stock, percent made on that stock and money made on that stock)
    # total_cash = how much cash the user have available
    # overall_cash = the amount of money the user have available + money in stocks
    # profit = profit in percentage
    # profitz = profit in money
def user_own(usernamex):
    username = usernamex
    rows = db.execute("SELECT * FROM :user", user = username)
    cash = db.execute("SELECT starting_cash FROM users WHERE username =:username", username = username)
    startingcash = float(cash[0]["starting_cash"])

    total_in_stocks = 0
    user_owns = []
    for row in rows:
        listx = []
        stock = row["stock"]
        company = lookup(stock)
        name = company["name"]
        pricex = company["price"]
        price = usd(pricex)
        listx.append(name)
        listx.append(stock)
        shares = int(row["shares"])
        listx.append(shares)
        avgbuyx = row["avgprice"]
        avgbuy = usd(avgbuyx)
        listx.append(avgbuy)
        listx.append(price)
        total_pricex = round(float(pricex * shares),2)
        total_in_stocks += total_pricex
        total_price = usd(total_pricex)
        listx.append(total_price)
        total_buy = round((shares * avgbuyx),2)
        percent_madex = (total_pricex - total_buy)*100 / total_buy
        percent_made = round((percent_madex),2)
        listx.append(percent_made)
        total_madex = total_pricex - total_buy
        total_made = usd(total_madex)
        listx.append(total_made)
        user_owns.append(listx)

    total_cashx = db.execute("SELECT cash FROM users WHERE username = :user", user = username)
    total_cashy = total_cashx[0]["cash"]
    total_cashz = round(total_cashy,2)
    total_cash = usd(total_cashz)

    overall_cashx = total_cashz + total_in_stocks
    overall_cash = usd(overall_cashx)

    profitx = (overall_cashx - startingcash)
    profitz = usd(profitx)
    percent = (profitx*100) / startingcash
    profit = round(percent,4)

    return(user_owns, total_cash, overall_cash, profit, profitz, profitx)


# search history
# no input
# output is history of the search engine
    # history = list of list of each stock searched on
    # one list in the history list = stock name, stock symbol, stock price and date searched on.
# this is to make it easier to find stocks by symbol.
def overall_history():
    x = db.execute("SELECT * FROM history")
    rows = sorted(x, key=itemgetter("searched"), reverse=True)

    history = []
    for row in rows:
        listx = []
        stock = row["stock"]
        listx.append(stock)
        symbol = row["symbol"]
        listx.append(symbol)
        pricex = row["price"]
        price = usd(pricex)
        listx.append(price)
        time = row["date"]
        listx.append(time)
        history.append(listx)


    return(history)

#gets top 10 searched on stocks
def tophistory():
    rows = db.execute("SELECT * FROM history")
    newlist = sorted(rows, key=itemgetter("searched"), reverse=True)

    list10 = []
    for row in range(10):
        listx = []
        stock = newlist[row]["stock"]
        listx.append(stock)
        symbol = newlist[row]["symbol"]
        listx.append(symbol)
        pricex = newlist[row]["price"]
        price = usd(pricex)
        listx.append(price)
        time = newlist[row]["date"]
        listx.append(time)

        list10.append(listx)

    return list10


# transaction history
# input username
# output is a list of list of each transaction made by that person
    # one transaction = stock symbol, how mane shares bought/sold, price per stock, total price of transaction, time of transaction
def transactions(username):
    x = db.execute("SELECT * FROM transactions WHERE username =:user", user = username)
    rows = sorted(x, key=itemgetter("time"), reverse=True)

    transactions = []
    for row in rows:
        listx = []
        stock = row["stock"]
        listx.append(stock)
        buy = int(row["buy"])
        if buy != 0:
            listx.append(buy)
        sell = int(row["sell"])
        if sell != 0:
            listx.append(sell)
        price_per_stockx = row["price_per_stock"]
        price_per_stock = usd(price_per_stockx)
        listx.append(price_per_stock)
        totalx = row["total_price"]
        total = usd(totalx)
        listx.append(total)
        time = row["time"]
        listx.append(time)

        transactions.append(listx)

    return transactions

# get ten most recent transactions
def toptransactions(username):
    x = db.execute("SELECT * FROM transactions WHERE username =:user", user = username)
    rows = sorted(x, key=itemgetter("time"), reverse=True)

    transactions = []
        # if it is 10 or more transactions, create a list of top 10
    if len(rows) > 9:
        for row in range(10):
            listx = []
            stock = rows[row]["stock"]
            listx.append(stock)
            buy = int(rows[row]["buy"])
            if buy != 0:
                listx.append(buy)
            sell = int(rows[row]["sell"])
            if sell != 0:
                listx.append(sell)
            price_per_stockx = rows[row]["price_per_stock"]
            price_per_stock = usd(price_per_stockx)
            listx.append(price_per_stock)
            totalx = rows[row]["total_price"]
            total = usd(totalx)
            listx.append(total)
            time = rows[row]["time"]
            listx.append(time)
            transactions.append(listx)
        # if there is 9 or fewer transactions made by the user, create a list with all of them
    else:
        for row in range(len(rows)):
            listx = []
            stock = rows[row]["stock"]
            listx.append(stock)
            buy = int(rows[row]["buy"])
            if buy != 0:
                listx.append(buy)
            sell = int(rows[row]["sell"])
            if sell != 0:
                listx.append(sell)
            price_per_stockx = rows[row]["price_per_stock"]
            price_per_stock = usd(price_per_stockx)
            listx.append(price_per_stock)
            totalx = rows[row]["total_price"]
            total = usd(totalx)
            listx.append(total)
            time = rows[row]["time"]
            listx.append(time)

            transactions.append(listx)

    return transactions

    # rank the users in terms of profit and create a list of the ranking from most profit to least.
def leaders():
    x = db.execute("SELECT * FROM users")
    rows = sorted(x, key=itemgetter("profitpercent"), reverse=True)

    leader = []
    rank = 0
    for row in rows:
        listx = []
        rank += 1
        listx.append(rank)
        username = row["username"]
        listx.append(username)
        cash = row["profit"]
        listx.append(cash)
        profit = row["profitpercent"]
        listx.append(profit)
        leader.append(listx)

    return leader

# create a list of top ten leaders from most profit to least profit.
def topleaders():
    x = db.execute("SELECT * FROM users")
    rows = sorted(x, key=itemgetter("profitpercent"), reverse=True)

    leader = []
    rank = 0
    for row in range(10):
        listx = []
        rank += 1
        listx.append(rank)
        username = rows[row]["username"]
        listx.append(username)
        cash = rows[row]["profit"]
        listx.append(cash)
        profit = rows[row]["profitpercent"]
        listx.append(profit)
        leader.append(listx)

    return leader

    # check every challenge if they have been completed. they are completed if they currently have value 1, then they need to be updated.
    # if a challenge is completed, we update the cash of the user and the startin_cash of the user to make the profit in terms of much cash they "started with"
    # if a challenge is completed we update the challenge to have the value 2, which means it can´t be completed again.
    # when the challenge is completed, the user will get money, so we update it as a transaction that the user receive money
def check_chal(username):
    cashx = db.execute("SELECT cash FROM users WHERE username = :user", user = username)
    cashy = cashx[0]["cash"]
    cashrn = round(cashy,2)

    scashx = db.execute("SELECT starting_cash FROM users WHERE username = :user", user = username)
    scashy = scashx[0]["starting_cash"]
    scashrn = round(scashy,2)

    rows = db.execute("SELECT * FROM challenges WHERE username = :user", user = username)
    c1,c2,c3,c4,c5,c6,c7 = rows[0]["c1"],rows[0]["c2"],rows[0]["c3"],rows[0]["c4"],rows[0]["c5"],rows[0]["c6"],rows[0]["c7"]
    c8,c9,c10,c11,c12 = rows[0]["c8"],rows[0]["c9"],rows[0]["c10"],rows[0]["c11"],rows[0]["c12"]

    if c1 == 1:
        db.execute("UPDATE users SET cash=:cash WHERE username=:user", cash = cashrn+1000, user=username)
        db.execute("UPDATE users SET starting_cash=:scash WHERE username=:user", scash = scashrn+1000, user=username)
        db.execute("UPDATE challenges SET c1 =:c1 WHERE username=:user", c1=2, user=username)
        db.execute("INSERT INTO transactions (username, buy, sell, stock, price_per_stock, total_price, time) VALUES (:user, :buy, :sell, :stock, :price, :total, :time)",
                user=username, buy=0, sell=0, stock="challenge 1 completed" , price=0, total=1000, time=datetime.datetime.now())
    if c2 == 1:
        db.execute("UPDATE users SET cash=:cash WHERE username=:user", cash = cashrn+1000, user=username)
        db.execute("UPDATE users SET starting_cash=:scash WHERE username=:user", scash = scashrn+1000, user=username)
        db.execute("UPDATE challenges SET c2 =:c2 WHERE username=:user", c2=2, user=username)
        db.execute("INSERT INTO transactions (username, buy, sell, stock, price_per_stock, total_price, time) VALUES (:user, :buy, :sell, :stock, :price, :total, :time)",
                user=username, buy=0, sell=0, stock="challenge 2 completed" , price=0, total=1000, time=datetime.datetime.now())
    if c3 == 1:
        db.execute("UPDATE users SET cash=:cash WHERE username=:user", cash = cashrn+1000, user=username)
        db.execute("UPDATE users SET starting_cash=:scash WHERE username=:user", scash = scashrn+1000, user=username)
        db.execute("UPDATE challenges SET c3 =:c3 WHERE username=:user", c3=2, user=username)
        db.execute("INSERT INTO transactions (username, buy, sell, stock, price_per_stock, total_price, time) VALUES (:user, :buy, :sell, :stock, :price, :total, :time)",
                user=username, buy=0, sell=0, stock="challenge 3 completed" , price=0, total=1000, time=datetime.datetime.now())
    if c4 == 1:
        db.execute("UPDATE users SET cash=:cash WHERE username=:user", cash = cashrn+2000, user=username)
        db.execute("UPDATE users SET starting_cash=:scash WHERE username=:user", scash = scashrn+2000, user=username)
        db.execute("UPDATE challenges SET c4 =:c4 WHERE username=:user", c4=2, user=username)
        db.execute("INSERT INTO transactions (username, buy, sell, stock, price_per_stock, total_price, time) VALUES (:user, :buy, :sell, :stock, :price, :total, :time)",
                user=username, buy=0, sell=0, stock="challenge 4 completed" , price=0, total=2000, time=datetime.datetime.now())
    if c5 == 1:
        db.execute("UPDATE users SET cash=:cash WHERE username=:user", cash = cashrn+1000, user=username)
        db.execute("UPDATE users SET starting_cash=:scash WHERE username=:user", scash = scashrn+1000, user=username)
        db.execute("UPDATE challenges SET c5 =:c5 WHERE username=:user", c5=2, user=username)
        db.execute("INSERT INTO transactions (username, buy, sell, stock, price_per_stock, total_price, time) VALUES (:user, :buy, :sell, :stock, :price, :total, :time)",
                user=username, buy=0, sell=0, stock="challenge 5 completed" , price=0, total=1000, time=datetime.datetime.now())
    if c6 == 1:
        db.execute("UPDATE users SET cash=:cash WHERE username=:user", cash = cashrn+2000, user=username)
        db.execute("UPDATE users SET starting_cash=:scash WHERE username=:user", scash = scashrn+2000, user=username)
        db.execute("UPDATE challenges SET c6 =:c6 WHERE username=:user", c6=2, user=username)
        db.execute("INSERT INTO transactions (username, buy, sell, stock, price_per_stock, total_price, time) VALUES (:user, :buy, :sell, :stock, :price, :total, :time)",
                user=username, buy=0, sell=0, stock="challenge 6 completed" , price=0, total=2000, time=datetime.datetime.now())
    if c7 == 1:
        db.execute("UPDATE users SET cash=:cash WHERE username=:user", cash = cashrn+3000, user=username)
        db.execute("UPDATE users SET starting_cash=:scash WHERE username=:user", scash = scashrn+3000, user=username)
        db.execute("UPDATE challenges SET c7 =:c7 WHERE username=:user", c7=2, user=username)
        db.execute("INSERT INTO transactions (username, buy, sell, stock, price_per_stock, total_price, time) VALUES (:user, :buy, :sell, :stock, :price, :total, :time)",
                user=username, buy=0, sell=0, stock="challenge 7 completed" , price=0, total=3000, time=datetime.datetime.now())
    if c8 == 1:
        db.execute("UPDATE users SET cash=:cash WHERE username=:user", cash = cashrn+2000, user=username)
        db.execute("UPDATE users SET starting_cash=:scash WHERE username=:user", scash = scashrn+2000, user=username)
        db.execute("UPDATE challenges SET c8 =:c8 WHERE username=:user", c8=2, user=username)
        db.execute("INSERT INTO transactions (username, buy, sell, stock, price_per_stock, total_price, time) VALUES (:user, :buy, :sell, :stock, :price, :total, :time)",
                user=username, buy=0, sell=0, stock="challenge 8 completed" , price=0, total=2000, time=datetime.datetime.now())
    if c9 == 1:
        db.execute("UPDATE users SET cash=:cash WHERE username=:user", cash = cashrn+2000, user=username)
        db.execute("UPDATE users SET starting_cash=:scash WHERE username=:user", scash = scashrn+2000, user=username)
        db.execute("UPDATE challenges SET c9 =:c9 WHERE username=:user", c9=2, user=username)
        db.execute("INSERT INTO transactions (username, buy, sell, stock, price_per_stock, total_price, time) VALUES (:user, :buy, :sell, :stock, :price, :total, :time)",
                user=username, buy=0, sell=0, stock="challenge 9 completed" , price=0, total=2000, time=datetime.datetime.now())
    if c10 == 1:
        db.execute("UPDATE users SET cash=:cash WHERE username=:user", cash = cashrn+2000, user=username)
        db.execute("UPDATE users SET starting_cash=:scash WHERE username=:user", scash = scashrn+2000, user=username)
        db.execute("UPDATE challenges SET c10 =:c10 WHERE username=:user", c10=2, user=username)
        db.execute("INSERT INTO transactions (username, buy, sell, stock, price_per_stock, total_price, time) VALUES (:user, :buy, :sell, :stock, :price, :total, :time)",
                user=username, buy=0, sell=0, stock="challenge 10 completed" , price=0, total=2000, time=datetime.datetime.now())
    if c11 == 1:
        db.execute("UPDATE users SET cash=:cash WHERE username=:user", cash = cashrn+5000, user=username)
        db.execute("UPDATE users SET starting_cash=:scash WHERE username=:user", scash = scashrn+5000, user=username)
        db.execute("UPDATE challenges SET c11 =:c11 WHERE username=:user", c11=2, user=username)
        db.execute("INSERT INTO transactions (username, buy, sell, stock, price_per_stock, total_price, time) VALUES (:user, :buy, :sell, :stock, :price, :total, :time)",
                user=username, buy=0, sell=0, stock="challenge 11 completed" , price=0, total=5000, time=datetime.datetime.now())
    if c12 == 1:
        db.execute("UPDATE users SET cash=:cash WHERE username=:user", cash = cashrn+10000, user=username)
        db.execute("UPDATE users SET starting_cash=:scash WHERE username=:user", scash = scashrn+10000, user=username)
        db.execute("UPDATE challenges SET c12 =:c12 WHERE username=:user", c12=2, user=username)
        db.execute("INSERT INTO transactions (username, buy, sell, stock, price_per_stock, total_price, time) VALUES (:user, :buy, :sell, :stock, :price, :total, :time)",
                user=username, buy=0, sell=0, stock="challenge 12 completed" , price=0, total=10000, time=datetime.datetime.now())

    # update challenge 1,2,3,4 if they are completed, they are updated together since all have to do with transactions.
    # if any of the challenges are completed, the challenge get a temporary value of 1, which means it is updated and the chekc_chal function has to do its job.
def update_c1234(username):
    rows = db.execute("SELECT * FROM challenges WHERE username = :user", user = username)
    c1 = rows[0]["c1"]
    c2 = rows[0]["c2"]
    c3 = rows[0]["c3"]
    c4 = rows[0]["c4"]

    rows = db.execute("SELECT * FROM transactions WHERE username =:user", user = username)
    if len(rows) > 0 and c1 !=2 :
        db.execute("UPDATE challenges SET c1 =:c1 WHERE username=:user", c1=1, user=username)
    if len(rows) > 9 and c2 !=2:
        db.execute("UPDATE challenges SET c2 =:c2 WHERE username=:user", c2=1, user=username)
    if len(rows) > 29 and c3!=2:
        db.execute("UPDATE challenges SET c3 =:c3 WHERE username=:user", c3=1, user=username)
    if len(rows) > 99 and c4 !=2:
        db.execute("UPDATE challenges SET c4 =:c4 WHERE username=:user", c4=1, user=username)

    # check if challenge 5 is completed
def update_c5(username):
    rows = db.execute("SELECT * FROM challenges WHERE username = :user", user = username)
    c5= rows[0]["c5"]

    rows = db.execute("SELECT best_rank FROM users WHERE username=:user", user=username)
    row = rows[0]["best_rank"]
    if row <= 10 and c5 != 2:
        db.execute("UPDATE challenges SET c5 =:c5 WHERE username=:user", c5=1, user=username)

    # check if challenge 6 is completed
def update_c6(username):
    rows = db.execute("SELECT * FROM challenges WHERE username = :user", user = username)
    c6=rows[0]["c6"]

    rows = db.execute("SELECT best_rank FROM users WHERE username=:user", user=username)
    row = rows[0]["best_rank"]
    if row <= 3 and c6 != 2:
        db.execute("UPDATE challenges SET c6 =:c6 WHERE username=:user", c6=1, user=username)

    # check if challenge 7 is completed
def update_c7(username):
    rows = db.execute("SELECT * FROM challenges WHERE username = :user", user = username)
    c7 = rows[0]["c7"]

    rows = db.execute("SELECT best_rank FROM users WHERE username=:user", user=username)
    row = rows[0]["best_rank"]
    if row == 1 and c7 != 2:
        db.execute("UPDATE challenges SET c7 =:c7 WHERE username=:user", c7=1, user=username)

    # check if challenge 8,9,10,11,12 is completed
def update_c8_12(username):
    rows = db.execute("SELECT * FROM challenges WHERE username = :user", user = username)
    c8,c9,c10,c11,c12= rows[0]["c8"],rows[0]["c9"],rows[0]["c10"],rows[0]["c11"],rows[0]["c12"]

    maxxx = db.execute("SELECT max FROM users WHERE username=:user", user=username)
    maxx = maxxx[0]["max"]
    minnn = db.execute("SELECT min FROM users WHERE username=:user", user=username)
    minn = minnn[0]["min"]


    if maxx >= 10 and c8 != 2:
        db.execute("UPDATE challenges SET c8 =:c8 WHERE username=:user", c8=1, user=username)
    if maxx >= 25 and c10 != 2:
        db.execute("UPDATE challenges SET c10 =:c10 WHERE username=:user", c10=1, user=username)
    if maxx >= 50 and c11 != 2:
        db.execute("UPDATE challenges SET c11 =:c11 WHERE username=:user", c11=1, user=username)
    if maxx >= 100 and c12 != 2:
        db.execute("UPDATE challenges SET c12 =:c12 WHERE username=:user", c12=1, user=username)
    if minn <= -20 and c9 != 2:
        db.execute("UPDATE challenges SET c9 =:c9 WHERE username=:user", c9=1, user=username)

    # get a list of the value of each challenge, so we can update the webpage.
def chalnum(username):
    rows = db.execute("SELECT * FROM challenges WHERE username = :user", user=username)
    chal=[]
    for row in rows:
        c1 = row["c1"]
        chal.append(c1)
        c2 = row["c2"]
        chal.append(c2)
        c3 = row["c3"]
        chal.append(c3)
        c4 = row["c4"]
        chal.append(c4)
        c5 = row["c5"]
        chal.append(c5)
        c6 = row["c6"]
        chal.append(c6)
        c7 = row["c7"]
        chal.append(c7)
        c8 = row["c8"]
        chal.append(c8)
        c9 = row["c9"]
        chal.append(c9)
        c10 = row["c10"]
        chal.append(c10)
        c11 = row["c11"]
        chal.append(c11)
        c12 = row["c12"]
        chal.append(c12)
    return(chal)

    # update challenges 12 times. idk why, it worked at one point.
def check_chal12(username):
    check_chal(username)
    check_chal(username)
    check_chal(username)
    check_chal(username)
    check_chal(username)
    check_chal(username)
    check_chal(username)
    check_chal(username)
    check_chal(username)
    check_chal(username)
    check_chal(username)
    check_chal(username)