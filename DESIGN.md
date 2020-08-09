I have commented all the files, so look at that as well.

style:
- to style my webpage I used the CSS we got from pset 9. I tried to use something else, but after talking to my cs50 final project TA, we couldn´t find out
why the new styling wouldn´t work. however, the VSS we got from pset9 looks good and works really well.
- on top of that I used some bootstrap to make my alert messages. they have som nice colours that fit the webpage quite well.
- since I was satisfied with the design and styling, I made the decition to focus more on the application and the coding inside the webpage.

html:
- my html code is pretty straight forward. I generally use simple html to display the text I want as structured and satisfying to the eye as possible.
- I use some javascript in the html code as well. nothing revolutionary, just some simple javascript to make the sell button be unclickable unless
some form is filled with user input.
- what my html code evolves the most about is variables given from application.py. I use these variables I created with for loops to to display lists of
stocks that the user owns, the stocks in the search database, the transactions made, the leaderboard etc. I combine this with some if´s and else´s to
change the style of some of the information I want to display. f.ex to change the colour of the profit made by a user from green to red if the profit
goes from positive to negative.
- alert system: my alert system in terms of errors or success messages works in a way that if you get an error or complete a transaction, the application.py
return you to another or the same webpage with a variable(a number). each number represents an alert. so if you try to login but you typed the wrong password,
you will be sent to the login page again, but with the variable 3, which will give the alert message "nvalid username and/or password". this system is something
I have used on a lot of my pages, because it worked and I found it simple. this alert system is a bunch of if and elses in terms of html code, that reads
a variable given in application.py

SQL:
I have created a bunch of databases to keep trak of information. I also use a lot of SQL in application.py to get variables and information, to update and put
in information. the tables I have created us:
- users{
    id INTEGER AUTOINCREMENT    (user id)
    username TEXT NOT NULL      (username)
    hash TEXT NOT NULL          (hashed password)
    cash FLOAT                  (keeps track of current available cash to trade for)
    profit FLOAT                (keeps track of current profit in cash)
    profitpercent FLOAT         (keeps track of current profit in percent)
    starting_cash INT           (keeps track of how much cash the user has been given, so all the cash not earned from the market. makes it easier to calculate profit after completing challenges f.ex)
    max FLOAT                   (keeps track of the users highest profit in percent ever)
    min FLOAT                   (keeps track of the users lowest profit in percent ever)
    best_rank INT               (keeps track of the users best ranking in history)
}
- transactions{
    username TEXT NOT NULL      (username)
    buy INT                     (how many shares bought if bought. if the transaction was of type sell, then buy is 0)
    sell INT                    (how many shares sold if sold. if the transaction was of type buy, then sold is 0)
    stock TEXT                  (name of stock)
    price_per_stock FLOAT       (price per stock of the transaction)
    toal_price FLOAT            (total price of the transation)
    time DATETIME               (time of transactions)
}
- numbuser{
    number_of_users INT     (keep track of number of users of webpage)
}
- challenges{
    username TEXT NOT NULL      (username)
    c1 INT                      (keeps track of status of challenge 1)
    c2 INT                      (keeps track of status of challenge 2)
    c3 INT                      (keeps track of status of challenge 3)
    c4 INT                      (keeps track of status of challenge 4)
    c5 INT                      (keeps track of status of challenge 5)
    c6 INT                      (keeps track of status of challenge 6)
    c7 INT                      (keeps track of status of challenge 7)
    c8 INT                      (keeps track of status of challenge 8)
    c9 INT                      (keeps track of status of challenge 9)
    c10 INT                     (keeps track of status of challenge 10)
    c11 INT                     (keeps track of status of challenge 11)
    c11 INT                     (keeps track of status of challenge 12)
}
- {username, every user gets a table to keep track of current holdings} {
    stock TEXT NOT NULL     (name of stock)
    shares INT              (number of shares)
    avgprice FLOAT          (average buy price of each stock in of the type in the holding)
}


myfunctions.py
- myfunctions.py is where I created a lot of functions that repeated itselfs a bunch of times. these are function that create lists to display
in the html page, that was way easier and more organized to have in a seperat file.

application.py
- this is where the code and logic itself is handled. each webpage has its on function in application.py where everything is handled.
- checking for user error/mistake is typical thing in the code
- updating, insert into, delete, create SQL databases is also something that is done a lot. Select from a SQL database is also heavily used to get information
that is used throughout the function.
- returning error messages
- returning to webpages etc.

