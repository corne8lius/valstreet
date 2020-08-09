import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helpers import apology, login_required, lookup, usd
from myfunctions import user_name, user_own, overall_history, transactions, tophistory, toptransactions, leaders, topleaders, check_chal, update_c1234
from myfunctions import update_c5, update_c6, update_c7, update_c8_12, chalnum, check_chal12

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.jinja_env.filters["usd"] = usd

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///finance.db")

if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")




    # index page.
    # gets routed to after completing a transaction or loging in
@app.route("/")
@login_required
    # variable x trigger various alerts on the html page
def index(x = None):
        # if no x is given, it will be set as 0, and nothing special will happen
    if x is None:
        x = 0
        # if x is set, it will trigger an alert
    else:
        x = x

        # get username through the function user_name
    user_id = session["user_id"]
    username = user_name(user_id)

        # get a list of each stock the person own, total cash available, overall cash, profit in percent and profit in cash from function user_own
    user_owns, total_cash, overall_cash, profit, profitz, profitx = user_own(username)
    db.execute("UPDATE users SET profit = :profit WHERE username =:username", profit = round(profitx,2), username = username)
    db.execute("UPDATE users SET profitpercent = :percent WHERE username =:username", percent = round(profit,4), username = username)

        # update the best_rank position of the user, we need this to check if the user ever was on top 10,3 or 1 on the leaderboard.
        # then we check if the users current position is better than the users current best, if it is, we update the current best.
    currentbest1 = db.execute("SELECT best_rank FROM users where username = :user", user=username)
    currentbest = int(currentbest1[0]["best_rank"])
    leader = leaders()
    userrank = 0
    for row in leader:
        if row[1] == username:
            userrank = row[0]
    if userrank < currentbest:
        db.execute("UPDATE users SET best_rank = :best WHERE username =:username", best=userrank, username = username)

        # check if current profit is greater than the best ever profit and update if so
    currentmax1 = db.execute("SELECT max FROM users where username = :user", user=username)
    currentmax = currentmax1[0]["max"]
    if currentmax < profit:
        db.execute("UPDATE users SET max = :maxx WHERE username =:username", maxx = round(profit,4), username = username)

        # check if the current profit is less than the worst ever profit and update if so
    currentmin1 = db.execute("SELECT min FROM users where username = :user", user=username)
    currentmin =currentmin1[0]["min"]
    if currentmin > profit:
        db.execute("UPDATE users SET min = :minn WHERE username =:username", minn = round(profit,4), username = username)

        # update and check all the challenges, so if they have been completed, we add cash, update so they cant be done again etc.
    update_c1234(username)
    update_c5(username)
    check_chal(username)
    update_c6(username)
    check_chal(username)
    update_c7(username)
    update_c8_12(username)
    update_c8_12(username)
    update_c8_12(username)
    update_c8_12(username)

    check_chal12(username)

        # go to the index webpage, which uses all of this variables to show different things for different users
    return render_template("index.html",username = username, listx = user_owns, cash = total_cash, total = overall_cash, profit = profit, made = profitz, x = x)


    # buy page
    # gets routed to if you´ve made a mistake in the buying process
@app.route("/buy", methods=["GET", "POST"])
@login_required
    # same here, x variable trigger various alerts on the html page
def buy(x=None):
        # get username through user_name function
    user_id = session["user_id"]
    username = user_name(user_id)

        #get a lot of variables from the function user_own. We are only going to use total_cash
    user_owns, total_cash, overall_cash, profit, profitz, profitx = user_own(username)

        # Since buy are only getting routed back to itself, we know that if x is none we have not been routed to ourself. routin back is an error-message
    if x is None:
            # if request method is post, we have a lot of things going on
        if request.method == "POST":

                # check that a stock name is provided
            if not request.form.get("stock"):
                    # if not return error message on the buy page
                return buy(1)

                #check if number of shares is provided, that it is a digit, that it is a whole digit and that it is bigger or equal to 1.
                # if not, return error message on the buy page
            elif (request.form.get("shares")).isdigit() == False:
                return buy(2)
            elif not request.form.get("shares") or float(request.form.get("shares")) < 1 or float(request.form.get("shares")).is_integer() == False:
                return buy(2)

                # look up the company that user want to purchase. and prepare the number of shares the user want to buy
            company = request.form.get("stock")
            shares = int(request.form.get("shares"))
            stock = lookup(company)

                # if the company doesn´t exist, return error message on buy page
            if stock == None:
                return buy(3)

                # get the price and symbol of the stock
            price = stock["price"]
            total_price = round(float(price * shares),2)
            stock = stock["symbol"]

                # get the amount of money that the user have
            cash_list = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id = user_id)
            cash_available = round((cash_list[0]["cash"]),2)

                # check that the user have enough money to buy the number of stocks he want to but. if not, display error message on buy page
            if cash_available < total_price:
                return buy(4)

                # if all of this is good, we are ready to put in the transaction
            else:
                    # new cash available for user is calculated
                newcash = cash_available - total_price

                    # update users new cash in the user table
                db.execute("UPDATE users SET cash = :newcash WHERE id = :user_id;", newcash = newcash, user_id = user_id)
                    # insert the transaction into the transaction table
                    # transaction: username, buy, sell, stock, price_per_stock, total_price, time
                db.execute("INSERT INTO transactions (username, buy, sell, stock, price_per_stock, total_price, time) VALUES (:username, :buy, :sell, :stock, :price_per, :total_price, :time)",
                    username = username, buy = shares, sell = int(0), stock = stock,
                    price_per = round(float(price),2), total_price = float(total_price), time = datetime.datetime.now())

                    # update c1-c4 is completed
                update_c1234(username)
                    # check challenges if completed
                check_chal12(username)

                # if user already owns that stock, we update that stock in the users own table of stocks owned.
                rows = db.execute("SELECT * FROM :user WHERE stock =:stock", user = username, stock = stock)
                if len(rows) == 1:
                        # select the stock that the user own.
                    shares_own = db.execute("SELECT * FROM :user WHERE stock =:stock", user = username, stock = stock)
                        # new number of shares is the amount of shares owned + amount of shares bought
                    new_shares = shares_own[0]["shares"] + shares
                        # update the users table to put in the new amount of shares the user own of that stock
                    db.execute("UPDATE :user SET shares =:new_shares WHERE stock =:stock", user = username, new_shares = new_shares, stock = stock)
                        # calculate the average price of the stocks the user own. the average price is the already average price of the stocks the user have
                        # times the amount of stocks owned, plus the price and shares of the current transaction, divided by the new amount of shares
                    avgprice = round((((shares_own[0]["shares"] * shares_own[0]["avgprice"]) + (shares * price)) / (shares_own[0]["shares"] + shares)), 2)
                        # update the users table to put in the new average price of the shares of that stock
                    db.execute("UPDATE :user SET avgprice =:updateprice WHERE stock =:stock", user = username, updateprice = avgprice, stock = stock)

                    # if the user doesn´t own the stock, we add the stock to the users table as a new stock
                else:
                        # average price of the stock the user buy is the price of the stock as it is right now.
                    avg = price
                        # insert the new stock into the table with, stock name, number of shares and average price per stock
                    db.execute("INSERT INTO :user (stock, shares, avgprice) VALUES (:stock, :shares, :avg)", user = username, stock = stock, shares = shares, avg = avg)

                    #return to index page and alert the user that the transaction was completed
                return index(1)

            # if x is none and the method is get, we just show the buy page.
        else:
                # the buy page will show the top 10 companies that is searched on the most by all user of the webpage to make it easier to find
                # companies and the price, instead of gamblingthis information is collected through the tophistory function.
            history = tophistory()
                 # go to buy page with the information needed
            return render_template("buy.html",history = history, cash = total_cash)

        # if x is something else than None, we know that we have an error from the method ="POST" area, so we still show the buy page, but with the corresponding error message
    else:
            # history from tophistory function to make it easy to find stocks to buy
        history = tophistory()
            # go to buy page with alert message, depending on the x value
        return render_template("buy.html", history = history, cash = total_cash, x = x)



# history
@app.route("/history")
@login_required
def history():
        # gets username from the user_name function
    user_id = session["user_id"]
    username = user_name(user_id)
        # gets all transaction the user have made from the transactions function.
    transaction = toptransactions(username)

        # goes to history page with all transactions as a variable
    return render_template("history.html", transactions = transaction)



# login
# log in was made for us, the only thing I added was the alert system that I used on the other pages as well.
# the alert system consists of an variable x that gets passed through the function again
@app.route("/login", methods=["GET", "POST"])
def login(x = None):
        # clear login information
    session.clear()
        # checks if x is none
    if x is None:
            # if rewuest method is post
        if request.method == "POST":
                # Ensure username was submitted
            if not request.form.get("username"):
                return login(1)
                # Ensure password was submitted
            elif not request.form.get("password"):
                return login(2)
                # Query database for username
            rows = db.execute("SELECT * FROM users WHERE username = :username",
                              username=request.form.get("username"))
                # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
                return login(3)
                # Remember which user has logged in
            session["user_id"] = rows[0]["id"]

                # Redirect user to home page if successful login
            return index(3)

            # if method is get, login webpage is shown
        else:
            return render_template("login.html")
        #if x is not none, that means an error message has occured, and it will be displayed on the login page.
    else:
        return render_template("login.html", x = x)


#logout
@app.route("/logout")
def logout():
        # Forget any user_id
    session.clear()
        # Redirect user to login form
    return redirect("/")


    # quote
    # same alert system as previous
@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote(x = None):
        # get history and top10 most searched companies from the overall_history and tophistory functions. we use them on the webpage we display.
    history = overall_history()
    top10 = tophistory()

    if x is None:
            # if request is post, we want to look up a stock.
        if request.method == "POST":
                # check if the user actually have written anything in the stock form, if not give an alert message
            if not request.form.get("symbol"):
                return quote(2)

                # save the users input in the variable company
            company = request.form.get("symbol")

                # select from history any companies that is like the user imput. this makes the search engine look up companies that is similar to
                # the user input. f.ex "net" will give cloudfare which have symbol"NET", netflix and netapp.
                # I know there is a possibility for an SQL injection here, but I didn´t figure out any other ways to do it.
            historyq = db.execute(f"SELECT * FROM history WHERE stock LIKE '%{company}%'")

                # we use the lookup function we got to see if there is a company with the exact user input. so if there is a company with symbol/ticker
                # that matches the exact user input. this is useful because it makes the stock list display the company that matches this if it is one,
                # and add companies with that ticker to our database if it doesn´t exist.
            stockx = lookup(company)

                # if there is no company with a symbol that matches the user input and no company in our database with similar name, display alert message
            if stockx == None and len(historyq) < 1:
                # Return apology("couldn't find a stock, try again", 403)
                return quote(1)


                # if we found a stock with exact same symbol as user input, add it to the list stocks, if not the list stocks is empty
            stocks = [stockx] if stockx is not None else []
                # we only want to display at most 10 result. this is to make the time it take to find the stocks searched for less. also giving a better list
                # of companies. if the list is not what the user want, the user should specify the search more.
            for stock in historyq[:10]:
                    # if a stock with the exact symbol is already in our database, continue. we have already added it, because it is stockx
                if stockx is not None and stock['symbol'] == stockx['symbol']:
                    continue

                    # add all stock that is similar to the user input to the stocks list that we will display when the user search.
                stocks.append(lookup(stock['symbol']))

                # run forloop to insert new stocks that we the lookup function found to our database
                # or update prices of companies that already is in our database.
                # we also update the amount of times each stock have been searched upon, so that we can make the top10 searched list
            for stock in stocks:
                symbol = stock["symbol"]
                price = stock["price"]
                name = stock["name"]
                stock_history = db.execute("SELECT * FROM history WHERE symbol =:symbol", symbol=symbol)
                if len(stock_history) != 1:
                    db.execute("INSERT INTO history (stock, symbol, price, date, searched) VALUES (:stock, :symbol, :price, :date, :searched)",
                        stock=name, symbol=symbol, price=price, date=datetime.datetime.now(), searched=1)

                else:
                    searchedx = stock_history[0]["searched"]
                    db.execute("UPDATE history SET price =:price, date =:date, searched = :searched WHERE symbol=:symbol",
                        price=price, date=datetime.datetime.now(), searched=searchedx+1, symbol=symbol)

                # go to quoted with the stocks list. the stocks list will be displayed as the result of the users search.
            return render_template("quoted.html", stocks=stocks)

            # if methos is GET, display the top 10 most searched stocks as a list just to make it easier for the user to search.
        else:
            return render_template("quote.html", history=history, top10=top10, x=x)

    else:
        return render_template("quote.html", history=history, top10=top10, x=x)


    # register
    # same alert system as previous
@app.route("/register", methods=["GET", "POST"])
def register(x = None):
    if x is None:
        x = 0
        if request.method == "POST":

                # Ensure username was submitted
            if not request.form.get("username"):
                return register(1)

                # Ensure password was submitted
            elif not request.form.get("password"):
                return register(2)

                # Ensure confirm apssword was submitted
            elif not request.form.get("confirmation"):
                return register(3)

                # Ensure that passwords match
            elif request.form.get("password") != request.form.get("confirmation"):
                return register(4)

            rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

                # Ensure that user doesn't exist
            if len(rows) != 0:
                return register(5)

                # if the users attempt to register went through all of the above, the user is ready to register.
            else:
                    # update the number of users in the database
                numbuserx = db.execute("SELECT * FROM numbuser")
                numbuser = numbuserx[0]["number_of_users"]
                db.execute("UPDATE numbuser SET number_of_users =:num WHERE number_of_users =:numb", num = numbuser+1, numb = numbuser)

                    # update the users table with the username, hashed password, set best rank to last. give the user $10000 and set everything else to 0
                password = request.form.get("password")
                username = request.form.get("username")
                hash_pass =generate_password_hash(password)
                db.execute("INSERT INTO users (username, hash, profit, profitpercent, starting_cash, max, min, best_rank) VALUES (:username, :password, :profit, :percent, :cash, :maxx, :minn, :bestrank)",
                              username=username, password = hash_pass, profit = 0, percent = 0, cash = 10000, maxx =0, minn=0, bestrank = numbuser + 1)
                    # give the user an empty challenge table to complete all the challenges
                db.execute("INSERT INTO challenges(username, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12) VALUES (:username, :c1, :c2, :c3, :c4, :c5, :c6, :c7, :c8, :c9, :c10, :c11, :c12)",
                                username=username, c1=0, c2=0, c3=0, c4=0, c5=0, c6=0, c7=0, c8=0, c9=0, c10=0, c11=0,c12=0)
                    # create a new table for the user that keeps track of all the stock the user owns.
                db.execute("CREATE TABLE :user (stock TEXT NOT NULL, shares INTEGER, avgprice FLOAT)", user = username)
                    # return to the login page
                return login(4)
        else:
            return render_template("register.html", x = x)
    else:
        return render_template("register.html", x = x)


    # sell
    # same alert system as previous
@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell(x = None):
        # set username of the user, we are going to use it a lot
    user_id = session["user_id"]
    username = user_name(user_id)
    if x is None:
        if request.method == "POST":
                # check that the user have typed in a positive integer, in the shares field, if not return an alert
            if (request.form.get("shares1")).isdigit() == False:
                return sell(1)
            elif not request.form.get("shares1") or float(request.form.get("shares1")) < 1 or float(request.form.get("shares1")).is_integer() == False:
                return sell(1)
            if (request.form.get("symbol") == None):
                return sell(2)

                # get the company the user want to sell
            company = request.form.get("symbol")
            shares = int(request.form.get("shares1"))
            stock = lookup(company)

                # get the price of the stock
            price = stock["price"]
            total_price = round(float(price * shares), 2)
            stock = stock["symbol"]

                # check if user owns the number of shares he want to sell
                # we know the user owns the stock since it is a dropdown meny with the stocks the user owns.
            stock_own = db.execute("SELECT * FROM :user WHERE stock = :stock", user = username, stock = stock)
            shares_own = stock_own[0]["shares"]
            new_shares = shares_own - shares
            if new_shares < 0:
                return sell(4)

                # ready to sell the stock
                # if the user sells all the stocks he owns of that company, we most remove the company from the users table
            elif new_shares == 0:
                    # delete stock from user table
                db.execute("DELETE FROM :user WHERE stock =:stock", user = username, stock = stock)
                    # get the cash the user made from selling the stocks
                cash_list = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id = user_id)
                cash_available = cash_list[0]["cash"]
                newcash = cash_available + total_price
                    #update the cash the user have and insert the transaction into the transactions table
                db.execute("UPDATE users SET cash = :newcash WHERE id = :user_id;", newcash = newcash, user_id = user_id)
                db.execute("INSERT INTO transactions (username, buy, sell, stock, price_per_stock, total_price, time) VALUES (:username, :buy, :sell, :stock, :price_per, :total_price, :time)",
                    username = username, buy = int(0), sell = -shares, stock = stock,
                    price_per = round(float(price),2), total_price = float(total_price), time = datetime.datetime.now())

                    # update and check if the transactions challenges is completed
                update_c1234(username)
                check_chal12(username)

                    # return to index with an alert message of complete transaction
                return index(2)

                # if the user sell some of his shares we just update the user list
            else:
                    # update the users list to own fewer stocks of that stock
                db.execute("UPDATE :user SET shares =:new_shares WHERE stock =:stock", user = username, new_shares = new_shares, stock = stock)
                    # get the new cash the user now has
                cash_list = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id = user_id)
                cash_available = cash_list[0]["cash"]
                newcash = cash_available + total_price
                    # update the users cash and set the transaction into the transaction table.
                db.execute("UPDATE users SET cash = :newcash WHERE id = :user_id;", newcash = newcash, user_id = user_id)
                db.execute("INSERT INTO transactions (username, buy, sell, stock, price_per_stock, total_price, time) VALUES (:username, :buy, :sell, :stock, :price_per, :total_price, :time)",
                    username = username, buy = int(0), sell = -shares, stock = stock,
                    price_per = round(float(price),2), total_price = float(total_price), time = datetime.datetime.now())

                    # update and check if the transactions challenges is completed
                update_c1234(username)
                check_chal12(username)
                    # return to index with an alert message of complete transaction
                return index(2)

    # display sell page with variables needed
        else:
            user_owns, total_cash, overall_cash, profit, profitz, profitx = user_own(username)

            return render_template("sell.html", listx = user_owns, cash = total_cash, total = overall_cash, x = x)
    else:
        user_owns, total_cash, overall_cash, profit, profitz, profitx = user_own(username)

        return render_template("sell.html", listx = user_owns, cash = total_cash, total = overall_cash, x = x)

    # cash
    # only a webpage that display the challenges and if they are completed.
@app.route("/cash", methods=["GET", "POST"])
@login_required
def cash():
        # get username
    user_id = session["user_id"]
    username = user_name(user_id)
        # get the challenges with status from the chalnum function. 0=not completed, 1=completed and under process of being handled, 2=completed and finished
    chal = chalnum(username)
        #go to webpage with th
    return render_template("cash.html", chal=chal)

    # leaderboard
    # show the top 10 leaderboard table
@app.route("/leaderboard",  methods=["GET", "POST"])
@login_required
def leaderboard():
        # get username
    user_id = session["user_id"]
    username = user_name(user_id)
        # get the whole leaderboard
    leader = leaders()
        # get the top10 leaderboard
    topleader = topleaders()
        # find the users rank in leaderboard, so we can display the users rank.
    user = []
    for row in leader:
        if row[1] == username:
            user = row
        # return to the leaderboard table that display the top 10 and the user himself
    return render_template("leaderboard.html", leaders = topleader, user = user)

    # leaderboard2
    # show the whole leadeboard table
@app.route("/leaderboard2",  methods=["GET", "POST"])
@login_required
def leaderboard2():
        # get username
    user_id = session["user_id"]
    username = user_name(user_id)
        # get the whole leaderboard
    leader = leaders()
        # find the users rank in leaderboard, so we can display the users rank.
    user = []
    for row in leader:
        if row[1] == username:
            user = row
        # return to the leaderboard table that display the top 10 and the user himself
    return render_template("leaderboard2.html", leaders = leader, user = user)

    # help mage
    # display information (only text)
@app.route("/help",  methods=["GET", "POST"])
@login_required
def helpx():
        # go to help page
    return render_template("help.html")

    # quote2
    # original quote only display top ten most searched stocks, quote2 display all stock that already is searched
@app.route("/quote2",  methods=["GET", "POST"])
@login_required
def quote2():
        # get all stocks that is searched at least once
    history = overall_history()
        # go to quote2
    return render_template("quote2.html", history = history)

    # history2
    # original history shows only 10 most recent transactions, history2 shows all transactions
@app.route("/history2",  methods=["GET", "POST"])
@login_required
def history2():
        # get username
    user_id = session["user_id"]
    username = user_name(user_id)
        # get transactions from function
    toptrans = transactions(username)
        # go to history2
    return render_template("history2.html", transactions = toptrans)


def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
