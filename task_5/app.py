from flask import Flask, request, render_template_string, session, redirect, url_for
import psycopg2
import hashlib
import os
from datetime import datetime
import re
import secrets

app = Flask(__name__)
# Generate a proper secret key
app.secret_key = secrets.token_hex(32)  # More secure than hardcoded key

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="dpg-d0pm1k6uk2gs739qdm50-a.oregon-postgres.render.com",
            user="my_db_zt1o_user", 
            password="yoNx6WsiUAgIx5XuOO0MjaumivAeiC6Z",
            database="my_db_zt1o",
            port=5432,
            sslmode='require',
            connect_timeout=10
        )
        print("Database connected successfully!")
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Initialize database tables
def init_database():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Drop existing tables if they exist (for fresh start)
            cursor.execute("DROP TABLE IF EXISTS user_sessions CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS users CASCADE;")
            
            # Create users table
            cursor.execute("""
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100) NOT NULL,
                    phone VARCHAR(20),
                    is_verified BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    login_attempts INTEGER DEFAULT 0,
                    account_status VARCHAR(20) DEFAULT 'active'
                );
            """)
            
            # Create user sessions table
            cursor.execute("""
                CREATE TABLE user_sessions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    session_token VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                );
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id);")
            
            conn.commit()
            cursor.close()
            conn.close()
            print("Database initialized successfully!")
        except psycopg2.Error as e:
            print(f"Database initialization error: {e}")
            if conn:
                conn.rollback()
                conn.close()
    else:
        print("Failed to initialize database - no connection")

# Improved password hashing with salt
def hash_password(password):
    # Add salt for better security
    salt = "user_auth_salt_2025"
    return hashlib.sha256((password + salt).encode()).hexdigest()

# Email validation
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Phone validation
def is_valid_phone(phone):
    if not phone:
        return True  # Phone is optional
    pattern = r'^[\+]?[1-9]?[0-9]{7,15}$'
    return re.match(pattern, phone) is not None

# CSS Styles (enhanced)
HTML_STYLE = """
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }
    .container {
        background: white;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        width: 100%;
        max-width: 450px;
        animation: fadeIn 0.5s ease-in;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .header {
        text-align: center;
        margin-bottom: 30px;
    }
    .header h2 {
        color: #333;
        font-size: 28px;
        margin-bottom: 10px;
    }
    .header p {
        color: #666;
        font-size: 14px;
    }
    .form-group {
        margin-bottom: 20px;
    }
    .form-group label {
        display: block;
        margin-bottom: 8px;
        color: #333;
        font-weight: 500;
    }
    .form-group input {
        width: 100%;
        padding: 12px 15px;
        border: 2px solid #e1e1e1;
        border-radius: 8px;
        font-size: 16px;
        transition: all 0.3s;
    }
    .form-group input:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    .btn {
        width: 100%;
        padding: 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s;
    }
    .btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    .links {
        text-align: center;
        margin-top: 20px;
    }
    .links a {
        color: #667eea;
        text-decoration: none;
        font-weight: 500;
        margin: 0 10px;
    }
    .links a:hover {
        text-decoration: underline;
    }
    .message {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        text-align: center;
        animation: slideIn 0.3s ease-out;
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    .success {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .warning {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    .dashboard {
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        width: 100%;
        max-width: 600px;
        animation: fadeIn 0.5s ease-in;
    }
    .user-info {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #e9ecef;
    }
    .user-info h3 {
        color: #333;
        margin-bottom: 15px;
        font-size: 20px;
    }
    .info-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        padding-bottom: 12px;
        border-bottom: 1px solid #e1e1e1;
    }
    .info-item:last-child {
        border-bottom: none;
        margin-bottom: 0;
    }
    .info-label {
        font-weight: 600;
        color: #495057;
    }
    .info-value {
        color: #333;
        font-weight: 500;
    }
    .status-active {
        color: #28a745;
        font-weight: bold;
    }
    .status-inactive {
        color: #dc3545;
        font-weight: bold;
    }
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 15px;
        margin-bottom: 20px;
    }
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 2px solid #e9ecef;
        transition: all 0.3s;
    }
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .stat-number {
        font-size: 24px;
        font-weight: bold;
        color: #667eea;
    }
    .stat-label {
        color: #666;
        font-size: 14px;
        margin-top: 5px;
    }
</style>
"""

# Home route
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    return render_template_string(HTML_STYLE + '''
    <div class="container">
        <div class="header">
            <h2>🔐 User Authentication System</h2>
            <p>Secure Login & Registration with PostgreSQL</p>
        </div>
        <div style="text-align: center;">
            <a href="/register" style="text-decoration: none;">
                <button class="btn" style="margin-bottom: 15px;">📝 Create New Account</button>
            </a>
            <br>
            <a href="/login" style="text-decoration: none;">
                <button class="btn">🔑 Login to Account</button>
            </a>
        </div>
        <div class="links">
            <a href="/admin">⚙️ Admin Panel</a>
        </div>
    </div>
    ''')

# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data and clean it
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Comprehensive validation
        errors = []
        
        if not username:
            errors.append("Username is required")
        elif len(username) < 3:
            errors.append("Username must be at least 3 characters long")
        elif len(username) > 50:
            errors.append("Username cannot exceed 50 characters")
        
        if not email:
            errors.append("Email is required")
        elif not is_valid_email(email):
            errors.append("Please enter a valid email address")
        
        if not password:
            errors.append("Password is required")
        elif len(password) < 6:
            errors.append("Password must be at least 6 characters long")
        
        if password != confirm_password:
            errors.append("Passwords do not match")
        
        if not full_name:
            errors.append("Full name is required")
        elif len(full_name) < 2:
            errors.append("Full name must be at least 2 characters long")
        
        if phone and not is_valid_phone(phone):
            errors.append("Please enter a valid phone number or leave it blank")
        
        if errors:
            error_msg = "<br>• ".join(errors)
            return render_template_string(HTML_STYLE + f'''
            <div class="container">
                <div class="message error">
                    <h3>❌ Registration Failed</h3>
                    <p>• {error_msg}</p>
                </div>
                <div class="links">
                    <a href="/register">🔄 Try Again</a> | <a href="/">🏠 Home</a>
                </div>
            </div>
            ''')
        
        # Database operations
        conn = get_db_connection()
        if not conn:
            return render_template_string(HTML_STYLE + '''
            <div class="container">
                <div class="message error">
                    <h3>❌ Database Connection Error</h3>
                    <p>Could not connect to database. Please try again later.</p>
                </div>
                <div class="links">
                    <a href="/register">🔄 Try Again</a> | <a href="/">🏠 Home</a>
                </div>
            </div>
            ''')
        
        try:
            cursor = conn.cursor()
            
            # Check if username or email already exists
            cursor.execute("SELECT username, email FROM users WHERE username = %s OR email = %s", 
                          (username, email))
            existing_user = cursor.fetchone()
            
            if existing_user:
                cursor.close()
                conn.close()
                return render_template_string(HTML_STYLE + '''
                <div class="container">
                    <div class="message error">
                        <h3>❌ Registration Failed</h3>
                        <p>Username or email already exists. Please choose different credentials.</p>
                    </div>
                    <div class="links">
                        <a href="/register">🔄 Try Again</a> | <a href="/login">🔑 Login Instead</a>
                    </div>
                </div>
                ''')
            
            # Insert new user
            hashed_password = hash_password(password)
            cursor.execute("""
                INSERT INTO users (username, email, password, full_name, phone, is_verified, account_status) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (username, email, hashed_password, full_name, phone if phone else None, True, 'active'))
            
            user_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"User registered successfully: {username} (ID: {user_id})")
            
            return render_template_string(HTML_STYLE + f'''
            <div class="container">
                <div class="message success">
                    <h3>✅ Registration Successful!</h3>
                    <p>Welcome <strong>{full_name}</strong>! Your account has been created successfully.</p>
                    <hr style="margin: 15px 0; border: none; border-top: 1px solid #ccc;">
                    <p><strong>Username:</strong> {username}</p>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Account Status:</strong> Active & Verified</p>
                </div>
                <div class="links">
                    <a href="/login">🔑 Login Now</a> | <a href="/">🏠 Home</a>
                </div>
            </div>
            ''')
            
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
                conn.close()
            print(f"Registration database error: {e}")
            return render_template_string(HTML_STYLE + '''
            <div class="container">
                <div class="message error">
                    <h3>❌ Registration Failed</h3>
                    <p>Database error occurred. Please try again.</p>
                </div>
                <div class="links">
                    <a href="/register">🔄 Try Again</a> | <a href="/">🏠 Home</a>
                </div>
            </div>
            ''')
        except Exception as e:
            if conn:
                conn.close()
            print(f"Unexpected registration error: {e}")
            return render_template_string(HTML_STYLE + '''
            <div class="container">
                <div class="message error">
                    <h3>❌ Registration Failed</h3>
                    <p>An unexpected error occurred. Please try again.</p>
                </div>
                <div class="links">
                    <a href="/register">🔄 Try Again</a> | <a href="/">🏠 Home</a>
                </div>
            </div>
            ''')
    
    # GET request - show registration form
    return render_template_string(HTML_STYLE + '''
    <div class="container">
        <div class="header">
            <h2>📝 Create Account</h2>
            <p>Join our secure platform today</p>
        </div>
        <form method="POST" autocomplete="off">
            <div class="form-group">
                <label>👤 Username *</label>
                <input type="text" name="username" required maxlength="50" 
                       placeholder="Enter unique username">
            </div>
            <div class="form-group">
                <label>📧 Email Address *</label>
                <input type="email" name="email" required maxlength="100"
                       placeholder="your@email.com">
            </div>
            <div class="form-group">
                <label>🏷️ Full Name *</label>
                <input type="text" name="full_name" required maxlength="100"
                       placeholder="Your full name">
            </div>
            <div class="form-group">
                <label>📱 Phone Number (Optional)</label>
                <input type="tel" name="phone" maxlength="20" 
                       placeholder="+8801XXXXXXXXX or leave blank">
            </div>
            <div class="form-group">
                <label>🔒 Password *</label>
                <input type="password" name="password" required minlength="6"
                       placeholder="Minimum 6 characters">
            </div>
            <div class="form-group">
                <label>🔒 Confirm Password *</label>
                <input type="password" name="confirm_password" required minlength="6"
                       placeholder="Re-enter your password">
            </div>
            <button type="submit" class="btn">✨ Create Account</button>
        </form>
        <div class="links">
            <a href="/login">Already have an account? 🔑 Login</a><br><br>
            <a href="/">← Back to Home</a>
        </div>
    </div>
    ''')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username_or_email or not password:
            return render_template_string(HTML_STYLE + '''
            <div class="container">
                <div class="message error">
                    <h3>❌ Login Failed</h3>
                    <p>Please provide both username/email and password</p>
                </div>
                <div class="links">
                    <a href="/login">🔄 Try Again</a> | <a href="/register">📝 Create Account</a>
                </div>
            </div>
            ''')
        
        conn = get_db_connection()
        if not conn:
            return render_template_string(HTML_STYLE + '''
            <div class="container">
                <div class="message error">
                    <h3>❌ Database Connection Error</h3>
                    <p>Could not connect to database. Please try again.</p>
                </div>
                <div class="links">
                    <a href="/login">🔄 Try Again</a> | <a href="/">🏠 Home</a>
                </div>
            </div>
            ''')
        
        try:
            cursor = conn.cursor()
            hashed_password = hash_password(password)
            
            print(f"Login attempt for: {username_or_email}")
            
            # Check user credentials
            cursor.execute("""
                SELECT id, username, email, full_name, account_status, login_attempts, is_verified
                FROM users 
                WHERE (username = %s OR email = %s) AND password = %s
            """, (username_or_email, username_or_email.lower(), hashed_password))
            
            user = cursor.fetchone()
            
            if user:
                user_id, username, email, full_name, account_status, login_attempts, is_verified = user
                
                print(f"User found: {username} (ID: {user_id})")
                
                if account_status != 'active':
                    cursor.close()
                    conn.close()
                    return render_template_string(HTML_STYLE + '''
                    <div class="container">
                        <div class="message warning">
                            <h3>⚠️ Account Suspended</h3>
                            <p>Your account has been suspended. Please contact administrator.</p>
                        </div>
                        <div class="links">
                            <a href="/">🏠 Home</a>
                        </div>
                    </div>
                    ''')
                
                # Update login info
                cursor.execute("""
                    UPDATE users 
                    SET last_login = %s, login_attempts = 0 
                    WHERE id = %s
                """, (datetime.now(), user_id))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                # Set session
                session['user_id'] = user_id
                session['username'] = username
                session['full_name'] = full_name
                session['email'] = email
                
                print(f"Login successful for user: {username}")
                return redirect(url_for('dashboard'))
            
            else:
                print(f"Login failed for: {username_or_email}")
                
                # Increment failed login attempts
                cursor.execute("""
                    UPDATE users 
                    SET login_attempts = login_attempts + 1 
                    WHERE username = %s OR email = %s
                """, (username_or_email, username_or_email.lower()))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                return render_template_string(HTML_STYLE + '''
                <div class="container">
                    <div class="message error">
                        <h3>❌ Login Failed</h3>
                        <p>Invalid username/email or password. Please check your credentials and try again.</p>
                    </div>
                    <div class="links">
                        <a href="/login">🔄 Try Again</a> | <a href="/register">📝 Create Account</a>
                    </div>
                </div>
                ''')
                
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
                conn.close()
            print(f"Login database error: {e}")
            return render_template_string(HTML_STYLE + '''
            <div class="container">
                <div class="message error">
                    <h3>❌ Login Failed</h3>
                    <p>Database error occurred. Please try again.</p>
                </div>
                <div class="links">
                    <a href="/login">🔄 Try Again</a> | <a href="/">🏠 Home</a>
                </div>
            </div>
            ''')
        except Exception as e:
            if conn:
                conn.close()
            print(f"Unexpected login error: {e}")
            return render_template_string(HTML_STYLE + '''
            <div class="container">
                <div class="message error">
                    <h3>❌ Login Failed</h3>
                    <p>An unexpected error occurred. Please try again.</p>
                </div>
                <div class="links">
                    <a href="/login">🔄 Try Again</a> | <a href="/">🏠 Home</a>
                </div>
            </div>
            ''')
    
    # GET request - show login form
    return render_template_string(HTML_STYLE + '''
    <div class="container">
        <div class="header">
            <h2>🔑 Login</h2>
            <p>Access your secure account</p>
        </div>
        <form method="POST" autocomplete="off">
            <div class="form-group">
                <label>👤 Username or 📧 Email</label>
                <input type="text" name="username_or_email" required
                       placeholder="Enter username or email">
            </div>
            <div class="form-group">
                <label>🔒 Password</label>
                <input type="password" name="password" required
                       placeholder="Enter your password">
            </div>
            <button type="submit" class="btn">🚀 Login</button>
        </form>
        <div class="links">
            <a href="/register">Don't have an account? 📝 Register</a><br><br>
            <a href="/">← Back to Home</a>
        </div>
    </div>
    ''')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        return render_template_string(HTML_STYLE + '''
        <div class="container">
            <div class="message error">
                <h3>❌ Database Connection Error</h3>
                <p>Could not load dashboard. Please try again.</p>
            </div>
            <div class="links">
                <a href="/logout">🚪 Logout</a> | <a href="/">🏠 Home</a>
            </div>
        </div>
        ''')
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, email, full_name, phone, is_verified, 
                   created_at, last_login, login_attempts, account_status
            FROM users WHERE id = %s
        """, (session['user_id'],))
        
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user_data:
            username, email, full_name, phone, is_verified, created_at, last_login, login_attempts, account_status = user_data
            
            # Format dates
            created_date = created_at.strftime('%B %d, %Y at %I:%M %p') if created_at else 'Unknown'
            last_login_date = last_login.strftime('%B %d, %Y at %I:%M %p') if last_login else 'This is your first login!'
            
            return render_template_string(HTML_STYLE + f'''
            <div class="dashboard">
                <div class="header">
                    <h2>👤 Welcome, {full_name}!</h2>
                    <p>Your secure dashboard</p>
                </div>
                
                <div class="user-info">
                    <h3>📋 Account Information</h3>
                    <div class="info-item">
                        <span class="info-label">👤 Username:</span>
                        <span class="info-value">{username}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">🏷️ Full Name:</span>
                        <span class="info-value">{full_name}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">📧 Email:</span>
                        <span class="info-value">{email}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">📱 Phone:</span>
                        <span class="info-value">{phone if phone else 'Not provided'}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">🎯 Account Status:</span>
                        <span class="info-value status-{'active' if account_status == 'active' else 'inactive'}">
                            {account_status.upper()}
                        </span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">✅ Verified:</span>
                        <span class="info-value">{'✅ Yes' if is_verified else '❌ No'}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">📅 Member Since:</span>
                        <span class="info-value">{created_date}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">🕐 Last Login:</span>
                        <span class="info-value">{last_login_date}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">🔢 Login Attempts:</span>
                        <span class="info-value">{login_attempts}</span>
                    </div>
                </div>
                
                <div style="text-align: center;">
                    <a href="/logout" style="text-decoration: none;">
                        <button class="btn">🚪 Logout</button>
                    </a>
                </div>
            </div>
            ''')
        else:
            return redirect(url_for('logout'))
        
    except psycopg2.Error as e:
        if conn:
            conn.close()
        print(f"Dashboard database error: {e}")
        return render_template_string(HTML_STYLE + '''
        <div class="container">
            <div class="message error">
                <h3>❌ Error Loading Dashboard</h3>
                <p>Database error occurred. Please try logging in again.</p>
            </div>
            <div class="links">
                <a href="/logout">🚪 Logout</a> | <a href="/">🏠 Home</a>
            </div>
        </div>
        ''')
    except Exception as e:
        if conn:
            conn.close()
        print(f"Unexpected dashboard error: {e}")
        return render_template_string(HTML_STYLE + '''
        <div class="container">
            <div class="message error">
                <h3>❌ Error Loading Dashboard</h3>
                <p>An unexpected error occurred. Please try again.</p>
            </div>
            <div class="links">
                <a href="/logout">🚪 Logout</a> | <a href="/">🏠 Home</a>
            </div>
        </div>
        ''')

# Admin panel
@app.route('/admin')
def admin():
    conn = get_db_connection()
    if not conn:
        return render_template_string(HTML_STYLE + '''
        <div class="container">
            <div class="message error">
                <h3>❌ Database Connection Error</h3>
                <p>Could not connect to database</p>
            </div>
            <div class="links">
                <a href="/">🏠 Home</a>
            </div>
        </div>
        ''')
    
    try:
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_users,
                COUNT(CASE WHEN account_status = 'active' THEN 1 END) as active_users,
                COUNT(CASE WHEN is_verified = true THEN 1 END) as verified_users,
                COUNT(CASE WHEN last_login IS NOT NULL THEN 1 END) as logged_in_users
            FROM users
        """)
        stats = cursor.fetchone()
        
        # Get recent users
        cursor.execute("""
            SELECT username, email, full_name, account_status, 
                   created_at, last_login, login_attempts
            FROM users 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        recent_users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if stats:
            total_users, active_users, verified_users, logged_in_users = stats
        else:
            total_users = active_users = verified_users = logged_in_users = 0
        
        # Generate recent users HTML
        users_html = ""
        if recent_users:
            for user in recent_users:
                username, email, full_name, status, created_at, last_login, login_attempts = user
                created_str = created_at.strftime('%m/%d/%Y') if created_at else 'Unknown'
                last_login_str = last_login.strftime('%m/%d/%Y') if last_login else 'Never'
                
                users_html += f"""
                <div class="info-item">
                    <div>
                        <strong>{full_name}</strong> (@{username})<br>
                        <small style="color: #666;">{email}</small><br>
                        <small style="color: #888;">Attempts: {login_attempts} | Last: {last_login_str}</small>
                    </div>
                    <div style="text-align: right;">
                        <span class="status-{'active' if status == 'active' else 'inactive'}">{status.upper()}</span><br>
                        <small style="color: #888;">Joined: {created_str}</small>
                    </div>
                </div>
                """
        else:
            users_html = "<p style='text-align: center; color: #666;'>No users found</p>"
        
        return render_template_string(HTML_STYLE + f'''
        <div class="dashboard">
            <div class="header">
                <h2>⚙️ Admin Panel</h2>
                <p>System Overview & User Management</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{total_users}</div>
                    <div class="stat-label">Total Users</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #28a745;">{active_users}</div>
                    <div class="stat-label">Active Users</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #17a2b8;">{verified_users}</div>
                    <div class="stat-label">Verified Users</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #fd7e14;">{logged_in_users}</div>
                    <div class="stat-label">Ever Logged In</div>
                </div>
            </div>
            
            <div class="user-info">
                <h3>👥 Recent Users (Last 10)</h3>
                {users_html}
            </div>
            
            <div style="text-align: center;">
                <a href="/" style="text-decoration: none;">
                    <button class="btn">🏠 Back to Home</button>
                </a>
            </div>
        </div>
        ''')
        
    except psycopg2.Error as e:
        if conn:
            conn.close()
        print(f"Admin panel database error: {e}")
        return render_template_string(HTML_STYLE + '''
        <div class="container">
            <div class="message error">
                <h3>❌ Error Loading Admin Panel</h3>
                <p>Database error occurred. Please try again.</p>
            </div>
            <div class="links">
                <a href="/">🏠 Home</a>
            </div>
        </div>
        ''')
    except Exception as e:
        if conn:
            conn.close()
        print(f"Unexpected admin error: {e}")
        return render_template_string(HTML_STYLE + '''
        <div class="container">
            <div class="message error">
                <h3>❌ Error Loading Admin Panel</h3>
                <p>An unexpected error occurred. Please try again.</p>
            </div>
            <div class="links">
                <a href="/">🏠 Home</a>
            </div>
        </div>
        ''')

# Logout
@app.route('/logout')
def logout():
    username = session.get('username', 'Unknown')
    session.clear()
    print(f"User logged out: {username}")
    
    return render_template_string(HTML_STYLE + f'''
    <div class="container">
        <div class="message success">
            <h3>✅ Logged Out Successfully</h3>
            <p>You have been securely logged out. Thank you for using our platform!</p>
        </div>
        <div class="links">
            <a href="/login">🔑 Login Again</a> | <a href="/">🏠 Home</a>
        </div>
    </div>
    ''')

# Test database connection route
@app.route('/test-db')
def test_db():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            cursor.execute("SELECT COUNT(*) FROM users;")
            user_count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            return render_template_string(HTML_STYLE + f'''
            <div class="container">
                <div class="message success">
                    <h3>✅ Database Connection Successful</h3>
                    <p><strong>PostgreSQL Version:</strong><br>{version[0]}</p>
                    <p><strong>Total Users in Database:</strong> {user_count}</p>
                </div>
                <div class="links">
                    <a href="/">🏠 Home</a> | <a href="/admin">⚙️ Admin Panel</a>
                </div>
            </div>
            ''')
        except Exception as e:
            if conn:
                conn.close()
            return render_template_string(HTML_STYLE + f'''
            <div class="container">
                <div class="message error">
                    <h3>❌ Database Query Error</h3>
                    <p>Connected but query failed: {str(e)}</p>
                </div>
                <div class="links">
                    <a href="/">🏠 Home</a>
                </div>
            </div>
            ''')
    else:
        return render_template_string(HTML_STYLE + '''
        <div class="container">
            <div class="message error">
                <h3>❌ Database Connection Failed</h3>
                <p>Could not connect to PostgreSQL database</p>
            </div>
            <div class="links">
                <a href="/">🏠 Home</a>
            </div>
        </div>
        ''')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template_string(HTML_STYLE + '''
    <div class="container">
        <div class="message error">
            <h3>❌ Page Not Found</h3>
            <p>The page you're looking for doesn't exist.</p>
        </div>
        <div class="links">
            <a href="/">🏠 Home</a>
        </div>
    </div>
    '''), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template_string(HTML_STYLE + '''
    <div class="container">
        <div class="message error">
            <h3>❌ Internal Server Error</h3>
            <p>Something went wrong on our end. Please try again.</p>
        </div>
        <div class="links">
            <a href="/">🏠 Home</a>
        </div>
    </div>
    '''), 500

# Initialize database on startup
print("Initializing database...")
init_database()

# Run the application
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)