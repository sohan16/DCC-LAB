
from flask import Flask, request, redirect, render_template_string, session
import mysql.connector
import hashlib
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# MySQL config for freesqldatabase.com
DB_CONFIG = {
    'host': "db4free.net",
    'user': "sohanuser",
    'password': "Gz7#rP9dXqL!",
    'database': "userdbdemo"
}

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        print(f"DB Connection Error: {e}")
        return None

def init_db():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS users")
            cursor.execute("""
                CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password TEXT NOT NULL
                );
            """)
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print("DB Init Error:", e)
            conn.rollback()
            conn.close()
    return False

def hash_password(password):
    salt = "my_salt_123"
    return hashlib.sha256((password + salt).encode()).hexdigest()

@app.route('/')
def home():
    return '''
    <html>
    <head>
        <style>
            body {
                background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .box {
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
                text-align: center;
            }
            a {
                display: block;
                margin: 10px;
                text-decoration: none;
                font-weight: bold;
                color: #444;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Welcome</h2>
            <a href="/register">Register</a>
            <a href="/login">Login</a>
            <a href="/init-db">Reset DB</a>
        </div>
    </body>
    </html>
    '''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            if cursor.fetchone():
                return "User already exists"
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/login')
        return "DB connection failed"

    return '''
    <form method="POST">
        <h2>Register</h2>
        Username: <input name="username" required><br>
        Password: <input name="password" type="password" required><br>
        <button type="submit">Register</button>
    </form>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            if user:
                session['username'] = username
                return redirect('/dashboard')
            return "Invalid credentials"
        return "DB connection failed"

    return '''
    <form method="POST">
        <h2>Login</h2>
        Username: <input name="username" required><br>
        Password: <input name="password" type="password" required><br>
        <button type="submit">Login</button>
    </form>
    '''

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return f"<h2>Welcome, {session['username']}!</h2><br><a href='/logout'>Logout</a>"
    return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/init-db')
def reset_db():
    if init_db():
        return "Database reset successful"
    return "Failed to reset database"

if __name__ == '__main__':
    app.run(debug=True)
