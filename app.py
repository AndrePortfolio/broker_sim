import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd, valid_symbol, valid_shares, is_int

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Retrieve important info
    user_id, cash = get_user_id_and_cash()

    # Get user's porfolio
    portfolio, total = get_user_portfolio(user_id, cash)
    return render_template("index.html", portfolio=portfolio, total=total, cash=cash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        symbol_info = valid_symbol(request)
        if not symbol_info:
            return apology("invalid symbol", 400)

        shares = valid_shares(request)
        if not is_int(shares):
            return apology(shares, 400)

        # Retrieve important info
        user_id, cash = get_user_id_and_cash()
        price = symbol_info["price"]
        symbol = symbol_info["symbol"]

        # Calculate new balance
        if cash < price:
            return apology("Not enough balance", 400)
        else:
            new_balance = cash - (price * shares)

        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_balance, user_id)

        # Update porfolio
        output = db.execute("SELECT symbol FROM portfolio WHERE symbol = ? AND user_id = ?",
                            symbol, user_id)
        if not output:
            db.execute("INSERT INTO portfolio (symbol, quantity, user_id) VALUES (?, ?, ?)",
                       symbol, shares, user_id)
        else:
            db.execute("UPDATE portfolio SET quantity = (quantity + ?) WHERE symbol = ? AND user_id = ?",
                       shares, symbol, user_id)

        # Insert into history
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.execute("INSERT INTO history (symbol, shares, price, timestamp, user_id) VALUES (?, ?, ?, ?, ?)",
                   symbol, shares, price, timestamp, user_id)

        # Get user's porfolio
        portfolio, total = get_user_portfolio(user_id, new_balance, price, symbol)

        if shares == 1:
            flash(f"Bought {shares} share of {symbol} at ${price:.2f}.")
        else:
            flash(f"Bought {shares} shares of {symbol} at ${price:.2f} each.")

        return render_template("index.html", portfolio=portfolio, total=total, cash=new_balance)

    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]

    history = db.execute(
        "SELECT symbol, shares, price, timestamp FROM history WHERE user_id = ?", user_id)

    return render_template("history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol_info = valid_symbol(request)
        if not symbol_info:
            return apology("invalid symbol", 400)

        return render_template("quoted.html", the=symbol_info)

    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username:
            return apology("must provide username", 400)
        elif not password or not confirmation:
            return apology("must provide password", 400)
        elif password != confirmation:
            return apology("password missmatch", 400)

        # Hash the password for db security
        hash = generate_password_hash(password)
        try:
            new_user_id = db.execute(
                "INSERT INTO users (username, hash) VALUES (?,?)", username, hash)
        except ValueError:
            return apology("username already exists", 400)

        # Log in the user by storing their id in session
        session["user_id"] = new_user_id

        flash(f"Successfully Registered.")
        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # Retrieve important info
    user_id, cash = get_user_id_and_cash()
    symbols = db.execute("SELECT symbol FROM portfolio WHERE user_id = ?", user_id)

    if request.method == "POST":

        symbol_info = valid_symbol(request)
        if not symbol_info:
            return apology("invalid symbol", 400)

        shares_request = valid_shares(request)
        if not is_int(shares_request):
            return apology(shares_request, 400)

        price = symbol_info["price"]
        symbol = symbol_info["symbol"]

        user = db.execute("SELECT quantity FROM portfolio WHERE user_id = ? AND symbol = ?",
                          user_id, symbol)

        owned_shares = user[0]['quantity']

        # Calculate new balance
        if owned_shares < shares_request:
            return apology("Not enough shares", 400)
        # Remove from table
        elif owned_shares == shares_request:
            db.execute("DELETE FROM portfolio WHERE symbol = ? AND user_id = ?", symbol, user_id)
        # Update table
        else:
            db.execute("UPDATE portfolio SET quantity = (quantity - ?) WHERE symbol = ? AND user_id = ?",
                       shares_request, symbol, user_id)
        # Update Balance
        new_balance = cash + (price * shares_request)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_balance, user_id)

        # Insert into history
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        shares = -shares_request
        db.execute("INSERT INTO history (symbol, shares, price, timestamp, user_id) VALUES (?, ?, ?, ?, ?)",
                   symbol, shares, price, timestamp, user_id)

        # Get user's porfolio
        portfolio, total = get_user_portfolio(user_id, new_balance, price, symbol)

        if shares_request == 1:
            flash(f"Sold {shares_request} share of {symbol} at ${price:.2f}.")
        else:
            flash(f"Sold {shares_request} shares of {symbol} at ${price:.2f} each.")

        return render_template("index.html", portfolio=portfolio, total=total, cash=new_balance)

    return render_template("sell.html", symbols=symbols)


def get_user_id_and_cash():
    user_id = session["user_id"]
    user = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    if user is None:
        return apology("Session Error", 404)
    cash = user[0]['cash']

    return user_id, cash


def get_user_portfolio(user_id, cash, this_price=None, this_symbol=None):
    user_porfolio = db.execute("SELECT * FROM portfolio WHERE user_id = ?", user_id)
    portfolio = []
    total = 0
    for item in user_porfolio:
        shares = item['quantity']
        symbol = item['symbol']
        if symbol == this_symbol:
            price = this_price
        else:
            stock_info = lookup(symbol)
            price = stock_info['price']
        stock_total = float(price) * int(shares)
        total += stock_total
        portfolio.append({'symbol': symbol, 'price': price,
                         'shares': shares, 'stock_total': stock_total})

    total += cash
    return portfolio, total
