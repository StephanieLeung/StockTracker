from pathlib import Path
from flask import Flask, render_template, request, redirect, session, flash
from datetime import timedelta

from db_functions import *

# --- Global Variables -- #
DB_NAME = "stock_tracker.db"
FIRST_RUN = True

# checks if database exists
if (Path.cwd() / DB_NAME).exists():
    FIRST_RUN = False

# --- Flask --- #
app = Flask(__name__)
# sets session lifetime and secret key
app.secret_key = 'secret_key'
app.permanent_session_lifetime = timedelta(minutes=30)


@app.route('/', methods=['GET', 'POST'])
def loginPage():
    ALERT = ""
    if request.form:
        # saves form values to variables
        USERNAME = request.form.get("username")
        PASSWORD = request.form.get("password")
        if validateLogin(USERNAME, PASSWORD):
            USERNAME = getUsername(USERNAME)
            # creates a session for user
            session['username'] = USERNAME
            session.permanent = True
            return redirect(f'/portfolio/{USERNAME}')
        else:
            ALERT = "The username/password is invalid."
    return render_template("login.html", alert=ALERT)


@app.route('/signup', methods=['GET', 'POST'])
def signupPage():
    ALERT = ""
    if request.form:
        # saves form values to variables
        USERNAME = request.form.get("username")
        EMAIL = request.form.get("email")
        EMAIL = EMAIL.lower()
        PASSWORD = request.form.get("password")
        CONFIRM_PASSWORD = request.form.get("confirm_password")
        # checks if values for password and confirm password are the same
        if PASSWORD == CONFIRM_PASSWORD:
            if not getAccount(EMAIL, USERNAME):
                # adds user information to database
                addAccount(USERNAME, EMAIL, PASSWORD)
                # creates a session for user
                session['username'] = USERNAME
                session.permanent = True
                return redirect(f'/portfolio/{USERNAME}')
            else:
                ALERT = "An account with this username/email already exists"
        else:
            ALERT = "The passwords provided do not match"
    return render_template("signup.html", alert=ALERT)


@app.route('/portfolio/<string:username>', methods=['GET', 'POST'])
def portfolioPage(username):
    if checkSession(username):
        # creates 2D array with each stock's information
        STOCKS = tickerInformation(username)
        TOTAL_PROFIT = 0
        # calculates total profit
        for stock in STOCKS:
            TOTAL_PROFIT += calculateChange(stock)
        return render_template("portfolio.html", username=username, stocks=STOCKS, total_money=TOTAL_PROFIT)
    else:
        flash('Invalid session/Timed out.', 'dark')
        return redirect('/')


@app.route('/portfolio/<string:username>/add', methods=['GET', 'POST'])
def addSymbol(username):
    if checkSession(username):
        if request.form:
            session.modified = True
            # saves form values to variables
            SYMBOL = request.form.get("ticker_symbol").upper()
            PURCHASE_PRICE = float(request.form.get("purchase_price"))
            SHARES = float(request.form.get("shares"))
            if not checkTicker(username, SYMBOL):
                # adds stock information to database
                addStockInfo(username, SYMBOL, PURCHASE_PRICE, SHARES)
                # success message
                flash(f'{SYMBOL} successfully added to portfolio.', 'success')
            else:
                flash(f'{SYMBOL} already exists in your portfolio.', 'danger')
        return redirect(f'/portfolio/{username}')
    else:
        flash('Invalid session/Timed out.', 'dark')
        return redirect('/')


@app.route('/portfolio/<string:username>/edit', methods=['GET', 'POST'])
def editSymbol(username):
    if checkSession(username):
        if request.form:
            session.modified = True
            # saves form values to variables
            SYMBOL = request.form.get("ticker_symbol").upper()
            SHARES = float(request.form.get("shares"))
            # updates database information with form values
            updateStockInfo(username, SYMBOL, SHARES)
            # success message
            flash(f'{SYMBOL} successfully edited.', 'success')
        return redirect(f'/portfolio/{username}')
    else:
        flash('Invalid session/Timed out.', 'dark')
        return redirect('/')


@app.route('/portfolio/<string:username>/delete', methods=['GET', 'POST'])
def deleteSymbol(username):
    if checkSession(username):
        if request.form:
            session.modified = True
            # saves form values to variables
            SYMBOL = request.form.get("ticker_symbol").upper()
            # deletes stock information
            deleteStockInfo(username, SYMBOL)
            # success message
            flash(f'{SYMBOL} successfully deleted.', 'success')
        return redirect(f'/portfolio/{username}')
    else:
        flash('Invalid session/Timed out.', 'dark')
        return redirect('/')


@app.route('/portfolio/<string:username>/refresh')
def refreshPage(username):
    if checkSession(username):
        session.modified = True
        # reloads/ redirects to portfolio lage
        return redirect(f'/portfolio/{username}')
    flash('Invalid session/Timed out.', 'dark')
    return redirect('/')


@app.route('/deleteSession', methods=['GET', 'POST'])
def deleteSession():
    # deletes user's session
    session.pop('username', default=None)
    return redirect('/')


# --- Functions --- #
def checkSession(USERNAME):
    '''
    Checks if user is logged in or not
    :param USERNAME: (str)
    :return: (bool)
    '''
    if 'username' in session:
        if USERNAME in session['username']:
            return True
    return False


# --- Main Program Code --- #
if __name__ == "__main__":
    # create tables if database doesn't exist
    if FIRST_RUN:
        createTables()
    # runs web app
    app.run(debug=True)
    # use host="0.0.0.0" for public server
