from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import hashlib, os

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'loginsystem'

# Intialize MySQL
mysql = MySQL(app)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        rst = hashlib.md5(password.encode())
        epass = rst.hexdigest()
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, epass))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = '202cb962ac59075b964b07152d234b70'
            session['id'] = account['id']
            session['username'] = account['username']
            session['userrole'] = account['role']

            # Redirect to home page
            if session['userrole'] == 'admin':
                return redirect(url_for('admin'))
            elif session['userrole'] == 'normal':
                return redirect(url_for('home'))
            
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        rst = hashlib.md5(password.encode())
        epass = rst.hexdigest()
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', [username])
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts (`username`, `password`, `email`) VALUES ( %s, %s, %s)', (username, epass, email))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   session.pop('userrole', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/admin')
def admin():
    # Check if user is loggedin
    if session['loggedin'] == '202cb962ac59075b964b07152d234b70':
        if session['userrole']=='admin':
            # User is loggedin show them the home page
            return render_template('admin.html', username=session['username'],hello='Hlw Welcome')
        # User is not loggedin redirect to login page
        return redirect(url_for('login'))

@app.route('/home')
def home():
    # Check if user is loggedin
    if session['loggedin'] == '202cb962ac59075b964b07152d234b70':
        if session['userrole']=='normal':
            # User is loggedin show them the home page
            return render_template('home.html', username=session['username'])
        # User is not loggedin redirect to login page
        return redirect(url_for('login'))

@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run()