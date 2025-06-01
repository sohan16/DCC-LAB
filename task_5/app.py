
from flask import Flask, render_template_string, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL DB config (update with your own credentials)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yourpassword",
    database="userdb"
)
cursor = db.cursor()

HTML_STYLE = """<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%);
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }
    .container {
        background: white;
        padding: 40px;
        border-radius: 16px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.1);
        width: 100%;
        max-width: 460px;
    }
    .header { text-align: center; margin-bottom: 25px; }
    .header h2 { color: #222; font-size: 26px; }
    .form-group { margin-bottom: 20px; }
    .form-group label { color: #333; font-weight: 500; margin-bottom: 6px; display: block; }
    .form-group input {
        width: 100%;
        padding: 12px;
        border: 1.8px solid #ddd;
        border-radius: 10px;
        font-size: 15px;
    }
    .btn {
        width: 100%;
        padding: 12px;
        background: linear-gradient(135deg, #66a6ff, #536dfe);
        color: white;
        font-size: 16px;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        cursor: pointer;
    }
    .message {
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 15px;
    }
    .success { background: #e6f9f0; color: #2e7d32; border: 1px solid #b2dfdb; }
    .error { background: #fdecea; color: #c62828; border: 1px solid #f5c6cb; }
    .links { margin-top: 20px; text-align: center; }
    .links a { color: #1976d2; text-decoration: none; font-weight: 500; }
</style>"""

@app.route('/')
def index():
    return render_template_string(HTML_STYLE + '''
        <div class='container'>
            <div class='header'><h2>Login</h2></div>
            {% if message %}<div class='message error'>{{ message }}</div>{% endif %}
            <form method="POST" action="/login">
                <div class='form-group'>
                    <label>Username</label>
                    <input type="text" name="username" required>
                </div>
                <div class='form-group'>
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                <button class="btn" type="submit">Login</button>
            </form>
            <div class="links"><a href="/register">Don't have an account? Register</a></div>
        </div>
    ''', message=request.args.get('message'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
    result = cursor.fetchone()
    if result and check_password_hash(result[0], password):
        session['username'] = username
        return redirect('/dashboard')
    else:
        return redirect(url_for('index', message="Invalid credentials"))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        cursor.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username, email))
        if cursor.fetchone():
            return render_template_string(HTML_STYLE + '''
                <div class='container'>
                    <div class='header'><h2>Register</h2></div>
                    <div class='message error'>Username or Email already exists</div>
                    <div class='links'><a href="/">Back to Login</a></div>
                </div>''')

        cursor.execute("INSERT INTO users (fullname, email, username, password) VALUES (%s, %s, %s, %s)",
                       (fullname, email, username, password))
        db.commit()
        return redirect(url_for('index', message="Account created successfully"))

    return render_template_string(HTML_STYLE + '''
        <div class='container'>
            <div class='header'><h2>Register</h2></div>
            <form method="POST">
                <div class='form-group'><label>Full Name</label><input type="text" name="fullname" required></div>
                <div class='form-group'><label>Email</label><input type="email" name="email" required></div>
                <div class='form-group'><label>Username</label><input type="text" name="username" required></div>
                <div class='form-group'><label>Password</label><input type="password" name="password" required></div>
                <button class="btn" type="submit">Register</button>
            </form>
            <div class='links'><a href="/">Back to Login</a></div>
        </div>
    ''')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template_string(HTML_STYLE + f"<div class='container'><h2>Welcome, {session['username']}!</h2></div>")
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
