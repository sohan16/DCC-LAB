from flask import Flask, request, redirect, render_template_string, session, flash
import psycopg2
from psycopg2 import sql
import hashlib
import os
import logging

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Logging setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': "dpg-d0pm1k6uk2gs739qdm50-a.oregon-postgres.render.com",
    'user': "my_db_zt1o_user",
    'password': "yoNx6WsiUAgIx5XuOO0MjaumivAeiC6Z",
    'database': "my_db_zt1o",
    'port': 5432,
    'sslmode': 'require',
    'connect_timeout': 10
}

def get_db_connection():
    """Database connection with better error handling"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("Database connection successful")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        return None

def init_db():
    """Initialize database - DROP existing table and create new one"""
    max_retries = 3
    for attempt in range(max_retries):
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Drop existing table if exists (CAREFUL: This will delete all data)
                cursor.execute("DROP TABLE IF EXISTS users CASCADE;")
                
                # Create new table with all required fields
                cursor.execute("""
                    CREATE TABLE users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(100),
                        full_name VARCHAR(100),
                        phone VARCHAR(20),
                        password VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                conn.commit()
                cursor.close()
                conn.close()
                logger.info("Database initialized successfully")
                return True
                
            except psycopg2.Error as e:
                logger.error(f"Database initialization error: {e}")
                if conn:
                    conn.rollback()
                    conn.close()
        
        logger.warning(f"Database initialization attempt {attempt + 1} failed")
        if attempt < max_retries - 1:
            import time
            time.sleep(2)
    
    logger.error("Could not initialize database after multiple attempts")
    return False

def hash_password(password):
    """Enhanced password hashing with salt"""
    salt = "your_unique_salt_2024"  # Change this to a unique salt
    return hashlib.sha256((password + salt).encode()).hexdigest()

# Modern Dark Theme CSS
HTML_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --secondary: #f1f5f9;
        --accent: #06b6d4;
        --success: #10b981;
        --error: #ef4444;
        --warning: #f59e0b;
        --dark: #0f172a;
        --dark-card: #1e293b;
        --dark-border: #334155;
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        --shadow-lg: 0 35px 60px -12px rgba(0, 0, 0, 0.4);
    }
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
        position: relative;
        overflow-x: hidden;
    }
    
    /* Animated Background Elements */
    body::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 50%);
        animation: rotate 20s linear infinite;
        z-index: 1;
    }
    
    body::after {
        content: '';
        position: absolute;
        top: 20%;
        right: 10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(6, 182, 212, 0.15) 0%, transparent 70%);
        border-radius: 50%;
        animation: pulse 4s ease-in-out infinite;
        z-index: 1;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1) translateY(0px); opacity: 0.5; }
        50% { transform: scale(1.1) translateY(-10px); opacity: 0.8; }
    }
    
    .container {
        background: var(--dark-card);
        border: 1px solid var(--dark-border);
        padding: 48px 40px;
        border-radius: 24px;
        box-shadow: var(--shadow-lg);
        width: 100%;
        max-width: 450px;
        position: relative;
        z-index: 10;
        backdrop-filter: blur(20px);
        animation: slideInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    @keyframes slideInUp {
        0% {
            opacity: 0;
            transform: translateY(50px) scale(0.95);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    .logo {
        text-align: center;
        margin-bottom: 32px;
    }
    
    .logo-icon {
        font-size: 64px;
        margin-bottom: 16px;
        display: block;
        animation: bounce 2s infinite;
        filter: drop-shadow(0 4px 8px rgba(99, 102, 241, 0.3));
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-12px); }
        60% { transform: translateY(-6px); }
    }
    
    h1, h2 {
        color: var(--text-primary);
        text-align: center;
        font-weight: 700;
        margin-bottom: 12px;
        line-height: 1.2;
    }
    
    h1 { font-size: 32px; }
    h2 { font-size: 28px; }
    
    .subtitle {
        text-align: center;
        color: var(--text-secondary);
        font-size: 16px;
        margin-bottom: 40px;
        font-weight: 400;
    }
    
    .form-group {
        margin-bottom: 24px;
        position: relative;
    }
    
    .input-wrapper {
        position: relative;
    }
    
    input[type="text"], input[type="password"], input[type="email"] {
        width: 100%;
        padding: 18px 20px 18px 50px;
        border: 2px solid var(--dark-border);
        border-radius: 16px;
        font-size: 16px;
        font-weight: 400;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        background: rgba(15, 23, 42, 0.8);
        color: var(--text-primary);
        font-family: 'Poppins', sans-serif;
        outline: none;
    }
    
    input::placeholder {
        color: var(--text-secondary);
        font-weight: 400;
    }
    
    input:focus {
        border-color: var(--primary);
        background: rgba(15, 23, 42, 0.9);
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
        transform: translateY(-2px);
    }
    
    .input-icon {
        position: absolute;
        left: 18px;
        top: 50%;
        transform: translateY(-50%);
        color: var(--text-secondary);
        font-size: 18px;
        z-index: 2;
        transition: color 0.3s ease;
    }
    
    input:focus + .input-icon {
        color: var(--primary);
    }
    
    .btn {
        width: 100%;
        padding: 18px 24px;
        border: none;
        border-radius: 16px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        font-family: 'Poppins', sans-serif;
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        margin: 12px 0;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
    }
    
    .btn-primary:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(99, 102, 241, 0.4);
    }
    
    .btn-secondary {
        background: var(--dark-border);
        color: var(--text-primary);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .btn-secondary:hover {
        background: #475569;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    
    .btn-danger {
        background: linear-gradient(135deg, var(--error) 0%, #dc2626 100%);
        color: white;
        box-shadow: 0 8px 25px rgba(239, 68, 68, 0.3);
    }
    
    .btn-danger:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(239, 68, 68, 0.4);
    }
    
    .btn-warning {
        background: linear-gradient(135deg, var(--warning) 0%, #d97706 100%);
        color: white;
        box-shadow: 0 8px 25px rgba(245, 158, 11, 0.3);
    }
    
    .btn-warning:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(245, 158, 11, 0.4);
    }
    
    .link-group {
        text-align: center;
        margin-top: 32px;
    }
    
    .link {
        color: var(--text-secondary);
        text-decoration: none;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.3s ease;
        display: inline-block;
        margin: 8px 0;
    }
    
    .link:hover {
        color: var(--primary);
        transform: translateX(2px);
    }
    
    .message {
        padding: 24px;
        margin: 24px 0;
        border-radius: 20px;
        font-weight: 500;
        text-align: center;
        border: 1px solid;
        animation: slideInDown 0.6s ease-out;
    }
    
    @keyframes slideInDown {
        0% {
            opacity: 0;
            transform: translateY(-20px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .message-success {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
        color: #6ee7b7;
        border-color: rgba(16, 185, 129, 0.3);
    }
    
    .message-error {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%);
        color: #fca5a5;
        border-color: rgba(239, 68, 68, 0.3);
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin: 32px 0;
    }
    
    .stat-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid var(--dark-border);
        border-radius: 16px;
        padding: 24px 16px;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        border-color: var(--primary);
        box-shadow: 0 10px 25px rgba(99, 102, 241, 0.1);
    }
    
    .stat-icon {
        font-size: 32px;
        margin-bottom: 8px;
        display: block;
    }
    
    .stat-label {
        color: var(--text-secondary);
        font-size: 14px;
        font-weight: 500;
    }
    
    .button-grid {
        display: flex;
        flex-direction: column;
        gap: 16px;
        margin-top: 24px;
    }
    
    .button-grid a {
        text-decoration: none;
    }
    
    /* Floating particles */
    .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
        z-index: 1;
        pointer-events: none;
    }
    
    .particle {
        position: absolute;
        background: var(--primary);
        width: 4px;
        height: 4px;
        border-radius: 50%;
        opacity: 0.6;
        animation: float 8s infinite linear;
    }
    
    .particle:nth-child(1) { left: 10%; animation-delay: 0s; }
    .particle:nth-child(2) { left: 30%; animation-delay: 2s; }
    .particle:nth-child(3) { left: 50%; animation-delay: 4s; }
    .particle:nth-child(4) { left: 70%; animation-delay: 6s; }
    .particle:nth-child(5) { left: 90%; animation-delay: 1s; }
    
    @keyframes float {
        0% {
            bottom: -10px;
            transform: translateX(0px) rotate(0deg);
            opacity: 0;
        }
        10% {
            opacity: 0.6;
        }
        90% {
            opacity: 0.6;
        }
        100% {
            bottom: 100vh;
            transform: translateX(-50px) rotate(180deg);
            opacity: 0;
        }
    }
    
    /* Responsive */
    @media (max-width: 480px) {
        .container {
            padding: 32px 24px;
            margin: 16px;
        }
        
        h1 { font-size: 28px; }
        h2 { font-size: 24px; }
        
        .stats-grid {
            grid-template-columns: 1fr;
            gap: 16px;
        }
    }
</style>
"""

@app.route('/')
def index():
    return render_template_string(HTML_STYLE + '''
    <div class="particles">
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
    </div>
    <div class="container">
        <div class="logo">
            <span class="logo-icon">🌟</span>
            <h1>SecureHub</h1>
            <p class="subtitle">Your modern authentication portal</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-icon">🔐</span>
                <div class="stat-label">Secure</div>
            </div>
            <div class="stat-card">
                <span class="stat-icon">⚡</span>
                <div class="stat-label">Fast</div>
            </div>
            <div class="stat-card">
                <span class="stat-icon">🎯</span>
                <div class="stat-label">Simple</div>
            </div>
        </div>
        
        <div class="button-grid">
            <a href="/register">
                <button class="btn btn-primary">
                    <span>📝</span> Create New Account
                </button>
            </a>
            <a href="/login">
                <button class="btn btn-secondary">
                    <span>🔑</span> Login to Account
                </button>
            </a>
            <a href="/init-db">
                <button class="btn btn-warning">
                    <span>🔄</span> Reset Database
                </button>
            </a>
        </div>
    </div>
    ''')

@app.route('/register')
def register_page():
    return render_template_string(HTML_STYLE + '''
    <div class="particles">
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
    </div>
    <div class="container">
        <div class="logo">
            <span class="logo-icon">✨</span>
            <h2>Create Account</h2>
            <p class="subtitle">Join our secure platform today</p>
        </div>
        
        <form method="POST" action="/register">
            <div class="form-group">
                <div class="input-wrapper">
                    <input type="text" name="username" placeholder="Username (required)" required minlength="3">
                    <span class="input-icon">👤</span>
                </div>
            </div>
            <div class="form-group">
                <div class="input-wrapper">
                    <input type="email" name="email" placeholder="Email (optional)">
                    <span class="input-icon">📧</span>
                </div>
            </div>
            <div class="form-group">
                <div class="input-wrapper">
                    <input type="text" name="full_name" placeholder="Full Name (optional)">
                    <span class="input-icon">🏷️</span>
                </div>
            </div>
            <div class="form-group">
                <div class="input-wrapper">
                    <input type="text" name="phone" placeholder="Phone (optional)">
                    <span class="input-icon">📱</span>
                </div>
            </div>
            <div class="form-group">
                <div class="input-wrapper">
                    <input type="password" name="password" placeholder="Password (min 6 chars)" required minlength="6">
                    <span class="input-icon">🔒</span>
                </div>
            </div>
            <div class="form-group">
                <div class="input-wrapper">
                    <input type="password" name="confirm_password" placeholder="Confirm Password" required>
                    <span class="input-icon">🔐</span>
                </div>
            </div>
            <button type="submit" class="btn btn-primary">
                <span>🚀</span> Create Account
            </button>
        </form>
        
        <div class="link-group">
            <a href="/login" class="link">Already have an account? Login here</a><br>
            <a href="/" class="link">← Back to Home</a>
        </div>
    </div>
    ''')

@app.route('/login')
def login_page():
    return render_template_string(HTML_STYLE + '''
    <div class="particles">
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
    </div>
    <div class="container">
        <div class="logo">
            <span class="logo-icon">🔮</span>
            <h2>Welcome Back</h2>
            <p class="subtitle">Sign in to your account</p>
        </div>
        
        <form method="POST" action="/login">
            <div class="form-group">
                <div class="input-wrapper">
                    <input type="text" name="username" placeholder="Enter Username" required>
                    <span class="input-icon">👤</span>
                </div>
            </div>
            <div class="form-group">
                <div class="input-wrapper">
                    <input type="password" name="password" placeholder="Enter Password" required>
                    <span class="input-icon">🔒</span>
                </div>
            </div>
            <button type="submit" class="btn btn-primary">
                <span>🚀</span> Login
            </button>
        </form>
        
        <div class="link-group">
            <a href="/register" class="link">Need an account? Register here</a><br>
            <a href="/" class="link">← Back to Home</a>
        </div>
    </div>
    ''')

@app.route('/register', methods=['POST'])
def register():
    try:
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Input validation
        if not username or not password:
            return show_error("Please provide username and password")
        
        if len(username) < 3:
            return show_error("Username must be at least 3 characters long")
        
        if len(password) < 6:
            return show_error("Password must be at least 6 characters long")
        
        if password != confirm_password:
            return show_error("Passwords do not match")
        
        # Database operations
        conn = get_db_connection()
        if not conn:
            return show_error("Database connection failed. Please try again later.")
        
        try:
            cursor = conn.cursor()
            
            # Check if username exists
            cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return show_error("Username already exists. Please choose another one.")
            
            # Insert new user
            hashed_password = hash_password(password)
            cursor.execute("""
                INSERT INTO users (username, email, full_name, phone, password) 
                VALUES (%s, %s, %s, %s, %s)
            """, (username, email or None, full_name or None, phone or None, hashed_password))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"User {username} registered successfully")
            return show_success(f"Registration successful! Welcome {username}!", "/login", "Login Now")
            
        except psycopg2.Error as e:
            logger.error(f"Database error during registration: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return show_error("Registration failed due to database error. Please try again.")
            
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        return show_error("An unexpected error occurred. Please try again.")

@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            return show_error("Please provide both username and password")
        
        conn = get_db_connection()
        if not conn:
            return show_error("Database connection failed. Please try again later.")
        
        try:
            cursor = conn.cursor()
            hashed_password = hash_password(password)
            cursor.execute("SELECT username FROM users WHERE username = %s AND password = %s", 
                          (username, hashed_password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user:
                logger.info(f"User {username} logged in successfully")
                session['username'] = username
                return show_success(f"Welcome back {username}!", "/dashboard", "Go to Dashboard")
            else:
                return show_error("Invalid username or password")
                
        except psycopg2.Error as e:
            logger.error(f"Database error during login: {e}")
            if conn:
                conn.close()
            return show_error("Login failed due to database error. Please try again.")
            
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        return show_error("An unexpected error occurred. Please try again.")

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    
    username = session['username']
    return render_template_string(HTML_STYLE + '''
    <div class="particles">
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
    </div>
    <div class="container">
        <div class="logo">
            <span class="logo-icon">🎯</span>
            <h2>Dashboard</h2>
            <p class="subtitle">Welcome to your control center</p>
        </div>
        
        <div class="message message-success">
            <h3>🎉 Welcome, {}!</h3>
            <p>You are successfully logged in to your dashboard.</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-icon">✅</span>
                <div class="stat-label">Active</div>
            </div>
            <div class="stat-card">
                <span class="stat-icon">🔐</span>
                <div class="stat-label">Secure</div>
            </div>
            <div class="stat-card">
                <span class="stat-icon">🚀</span>
                <div class="stat-label">Ready</div>
            </div>
        </div>
        
        <div class="button-grid">
            <a href="/logout">
                <button class="btn btn-danger">
                    <span>🚪</span> Logout
                </button>
            </a>
            <a href="/">
                <button class="btn btn-secondary">
                    <span>🏠</span> Home
                </button>
            </a>
        </div>
    </div>
    '''.format(username))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return show_success("Logged out successfully", "/", "Go Home")

@app.route('/init-db')
def init_db_route():
    """Route to manually initialize database"""
    if init_db():
        return show_success("Database reset successfully!", "/", "Go Home")
    else:
        return show_error("Database reset failed. Please check logs.")

@app.route('/test-db')
def test_db():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return show_success(f"Database connected! Total users: {count}", "/", "Go Home")
        except Exception as e:
            return show_error(f"Database query failed: {str(e)}")
    else:
        return show_error("Database connection failed")

def show_success(message, link_url="/", link_text="Continue"):
    return render_template_string(HTML_STYLE + '''
    <div class="particles">
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
    </div>
    <div class="container">
        <div class="logo">
            <span class="logo-icon">🎉</span>
        </div>
        <div class="message message-success">
            <h3>Success!</h3>
            <p>{}</p>
        </div>
        <div class="button-grid">
            <a href="{}">
                <button class="btn btn-primary">{}</button>
            </a>
        </div>
    </div>
    '''.format(message, link_url, link_text))

def show_error(message):
    return render_template_string(HTML_STYLE + '''
    <div class="particles">
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
    </div>
    <div class="container">
        <div class="logo">
            <span class="logo-icon">❌</span>
        </div>
        <div class="message message-error">
            <h3>Error</h3>
            <p>{}</p>
        </div>
        <div class="button-grid">
            <a href="javascript:history.back()">
                <button class="btn btn-secondary">Try Again</button>
            </a>
            <a href="/">
                <button class="btn btn-primary">Go Home</button>
            </a>
        </div>
    </div>
    '''.format(message))

if __name__ == '__main__':
    print("Starting Flask application...")
    print("To reset database, visit: /init-db")
    print("To test database, visit: /test-db")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)