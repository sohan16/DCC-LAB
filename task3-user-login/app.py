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

HTML_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            position: relative;
            overflow: hidden;
        }
        
        body::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 40% 80%, rgba(120, 219, 255, 0.3) 0%, transparent 50%);
            animation: float 6s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-20px) rotate(1deg); }
        }
        
        .container {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 40px;
            border-radius: 24px;
            box-shadow: 
                0 25px 50px rgba(0, 0, 0, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
            width: 100%;
            max-width: 1200px;
            position: relative;
            z-index: 10;
            animation: slideUp 0.6s ease-out;
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            color: rgba(255, 255, 255, 0.95);
            margin-bottom: 8px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .header .subtitle {
            color: rgba(255, 255, 255, 0.7);
            font-size: 1.1rem;
            font-weight: 400;
        }
        
        .step-indicator {
            display: flex;
            justify-content: center;
            margin-bottom: 32px;
            gap: 16px;
        }
        
        .step {
            display: flex;
            align-items: center;
            padding: 10px 20px;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
            font-size: 0.9rem;
            font-weight: 500;
            color: rgba(255, 255, 255, 0.9);
        }
        
        .step.active {
            background: rgba(255, 255, 255, 0.25);
            border-color: rgba(255, 255, 255, 0.4);
        }
        
        .step-number {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.95);
        }
        
        .step.active .step-number {
            background: rgba(255, 255, 255, 0.4);
        }
        
        .form-section {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .dimensions-grid {
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            gap: 24px;
            align-items: center;
            margin-bottom: 24px;
        }
        
        .matrix-dims {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            text-align: center;
        }
        
        .matrix-dims h3 {
            color: rgba(255, 255, 255, 0.95);
            margin-bottom: 16px;
            font-size: 1.25rem;
            font-weight: 600;
        }
        
        .dim-inputs {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }
        
        .dim-input {
            width: 70px;
            padding: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            text-align: center;
            font-size: 1rem;
            font-weight: 500;
            background: rgba(255, 255, 255, 0.1);
            color: rgba(255, 255, 255, 0.9);
            transition: all 0.3s ease;
        }
        
        .dim-input:focus {
            border-color: rgba(255, 255, 255, 0.4);
            box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
            background: rgba(255, 255, 255, 0.15);
            outline: none;
        }
        
        .dim-label {
            font-size: 1rem;
            color: rgba(255, 255, 255, 0.7);
            font-weight: 500;
        }
        
        .multiplication-rule {
            text-align: center;
            background: rgba(255, 255, 255, 0.2);
            color: rgba(255, 255, 255, 0.95);
            padding: 12px;
            border-radius: 8px;
            font-weight: 500;
            font-size: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .matrix-section {
            display: grid;
            grid-template-columns: 1fr auto 1fr auto 1fr;
            gap: 16px;
            align-items: center;
            margin-bottom: 24px;
        }
        
        .matrix-container {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .matrix-title {
            text-align: center;
            margin-bottom: 16px;
            font-size: 1.25rem;
            color: rgba(255, 255, 255, 0.95);
            font-weight: 600;
        }
        
        .matrix-grid {
            display: grid;
            gap: 6px;
            justify-content: center;
        }
        
        .matrix-input {
            width: 50px;
            height: 50px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            text-align: center;
            font-size: 0.9rem;
            font-weight: 500;
            background: rgba(255, 255, 255, 0.1);
            color: rgba(255, 255, 255, 0.9);
            transition: all 0.3s ease;
        }
        
        .matrix-input:focus {
            border-color: rgba(255, 255, 255, 0.4);
            background: rgba(255, 255, 255, 0.15);
            box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
            outline: none;
        }
        
        .operation-symbol {
            text-align: center;
            font-size: 2rem;
            color: rgba(255, 255, 255, 0.9);
            font-weight: 700;
        }
        
        .btn {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%);
            color: rgba(255, 255, 255, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            backdrop-filter: blur(10px);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0.15) 100%);
            border-color: rgba(255, 255, 255, 0.3);
        }
        
        .btn-center {
            display: block;
            margin: 0 auto;
        }
        
        .result-section {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .result-title {
            font-size: 1.5rem;
            color: rgba(255, 255, 255, 0.95);
            margin-bottom: 24px;
            font-weight: 600;
        }
        
        .result-matrix {
            display: inline-block;
            background: rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .result-table {
            border-collapse: separate;
            border-spacing: 6px;
        }
        
        .result-table td {
            min-width: 60px;
            height: 50px;
            text-align: center;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%);
            color: rgba(255, 255, 255, 0.95);
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            display: table-cell;
            vertical-align: middle;
            padding: 4px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .result-table td:hover {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0.15) 100%);
        }
        
        .reset-btn {
            background: linear-gradient(135deg, rgba(255, 107, 107, 0.2) 0%, rgba(255, 142, 83, 0.2) 100%);
            color: rgba(255, 255, 255, 0.95);
            text-decoration: none;
            display: inline-block;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 107, 107, 0.3);
        }
        
        .reset-btn:hover {
            background: linear-gradient(135deg, rgba(255, 107, 107, 0.3) 0%, rgba(255, 142, 83, 0.3) 100%);
            transform: translateY(-2px);
            color: rgba(255, 255, 255, 0.95);
        }
        
        .error-message {
            background: linear-gradient(135deg, rgba(255, 107, 107, 0.2) 0%, rgba(255, 142, 83, 0.2) 100%);
            color: rgba(255, 255, 255, 0.95);
            padding: 16px;
            border-radius: 8px;
            text-align: center;
            font-weight: 500;
            margin: 16px 0;
            border: 1px solid rgba(255, 107, 107, 0.3);
        }
        
        .info-box {
            background: linear-gradient(135deg, rgba(132, 250, 176, 0.2) 0%, rgba(143, 211, 244, 0.2) 100%);
            color: rgba(255, 255, 255, 0.95);
            padding: 12px;
            border-radius: 8px;
            margin: 16px 0;
            text-align: center;
            font-weight: 500;
            border: 1px solid rgba(132, 250, 176, 0.3);
        }
        
        .floating-shapes {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            z-index: 1;
            pointer-events: none;
        }
        
        .shape {
            position: absolute;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            animation: floatUp 8s infinite linear;
        }
        
        .shape:nth-child(1) {
            width: 80px;
            height: 80px;
            left: 10%;
            animation-delay: 0s;
        }
        
        .shape:nth-child(2) {
            width: 120px;
            height: 120px;
            left: 20%;
            animation-delay: 2s;
        }
        
        .shape:nth-child(3) {
            width: 60px;
            height: 60px;
            left: 70%;
            animation-delay: 4s;
        }
        
        @keyframes floatUp {
            0% {
                bottom: -150px;
                transform: translateX(0px) rotate(0deg);
                opacity: 1;
            }
            100% {
                bottom: 100vh;
                transform: translateX(-100px) rotate(180deg);
                opacity: 0;
            }
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .container {
                padding: 16px;
                margin: 8px;
            }
            
            .header h1 {
                font-size: 1.75rem;
            }
            
            .dimensions-grid,
            .matrix-section {
                grid-template-columns: 1fr;
                gap: 16px;
            }
            
            .operation-symbol {
                font-size: 1.5rem;
                transform: rotate(90deg);
            }
            
            .step-indicator {
                flex-direction: column;
                align-items: center;
            }
            
            .matrix-input {
                width: 45px;
                height: 45px;
                font-size: 0.85rem;
            }
            
            .dim-inputs {
                flex-direction: column;
                gap: 12px;
            }
        }
    </style>
</head>
<body>
    <div class="floating-shapes">
        <div class="shape"></div>
        <div class="shape"></div>
        <div class="shape"></div>
    </div>
    <div class="container">
        <div class="header">
            <h1>🔢 Dynamic Matrix Multiplication</h1>
            <p class="subtitle">Multiply matrices of any compatible dimensions!</p>
        </div>

        <!-- Step Indicator -->
        <div class="step-indicator">
            <div class="step {{ 'active' if not (rows_a and cols_a and rows_b and cols_b) else '' }}">
                <div class="step-number">1</div>
                <span>Matrix Dimensions</span>
            </div>
            <div class="step {{ 'active' if (rows_a and cols_a and rows_b and cols_b) and not result else '' }}">
                <div class="step-number">2</div>
                <span>Enter Matrices</span>
            </div>
            <div class="step {{ 'active' if result else '' }}">
                <div class="step-number">3</div>
                <span>Result</span>
            </div>
        </div>

        {% if not (rows_a and cols_a and rows_b and cols_b) %}
        <!-- Step 1: Input matrix dimensions -->
        <div class="form-section">
            <form method="post">
                <div class="dimensions-grid">
                    <!-- Matrix A Dimensions -->
                    <div class="matrix-dims">
                        <h3>Matrix A Dimensions</h3>
                        <div class="dim-inputs">
                            <span class="dim-label">Rows:</span>
                            <input type="number" name="rows_a" min="1" max="10" class="dim-input" 
                                   placeholder="2" required value="{{ request.form.get('rows_a', '') }}">
                            <span class="dim-label">×</span>
                            <span class="dim-label">Cols:</span>
                            <input type="number" name="cols_a" min="1" max="10" class="dim-input" 
                                   placeholder="3" required value="{{ request.form.get('cols_a', '') }}">
                        </div>
                    </div>

                    <!-- Multiplication Rule -->
                    <div class="multiplication-rule">
                        <div>For A × B to be possible:</div>
                        <div><strong>Columns of A = Rows of B</strong></div>
                    </div>

                    <!-- Matrix B Dimensions -->
                    <div class="matrix-dims">
                        <h3>Matrix B Dimensions</h3>
                        <div class="dim-inputs">
                            <span class="dim-label">Rows:</span>
                            <input type="number" name="rows_b" min="1" max="10" class="dim-input" 
                                   placeholder="3" required value="{{ request.form.get('rows_b', '') }}">
                            <span class="dim-label">×</span>
                            <span class="dim-label">Cols:</span>
                            <input type="number" name="cols_b" min="1" max="10" class="dim-input" 
                                   placeholder="4" required value="{{ request.form.get('rows_b', '') }}">
                        </div>
                    </div>
                </div>

                <div class="info-box">
                    💡 Example: A(2×3) × B(3×4) = Result(2×4)
                </div>

                <button type="submit" name="submit_dimensions" class="btn btn-center">
                    📐 Generate Matrix Forms
                </button>
            </form>
        </div>
        {% endif %}

        {% if (rows_a and cols_a and rows_b and cols_b) and not result %}
        <!-- Step 2: Input matrices -->
        <div class="form-section">
            <form method="post">
                <input type="hidden" name="rows_a" value="{{ rows_a }}">
                <input type="hidden" name="cols_a" value="{{ cols_a }}">
                <input type="hidden" name="rows_b" value="{{ rows_b }}">
                <input type="hidden" name="cols_b" value="{{ cols_b }}">
                
                <div class="matrix-section">
                    <!-- Matrix A -->
                    <div class="matrix-container">
                        <h3 class="matrix-title">Matrix A ({{ rows_a }}×{{ cols_a }})</h3>
                        <div class="matrix-grid" style="grid-template-columns: repeat({{ cols_a }}, 1fr);">
                            {% for i in range(rows_a) %}
                                {% for j in range(cols_a) %}
                                    <input type="number" name="a{{i}}{{j}}" class="matrix-input" 
                                           placeholder="0" step="any" value="0">
                                {% endfor %}
                            {% endfor %}
                        </div>
                    </div>

                    <!-- Multiplication Symbol -->
                    <div class="operation-symbol">×</div>

                    <!-- Matrix B -->
                    <div class="matrix-container">
                        <h3 class="matrix-title">Matrix B ({{ rows_b }}×{{ cols_b }})</h3>
                        <div class="matrix-grid" style="grid-template-columns: repeat({{ cols_b }}, 1fr);">
                            {% for i in range(rows_b) %}
                                {% for j in range(cols_b) %}
                                    <input type="number" name="b{{i}}{{j}}" class="matrix-input" 
                                           placeholder="0" step="any" value="0">
                                {% endfor %}
                            {% endfor %}
                        </div>
                    </div>

                    <!-- Equals Symbol -->
                    <div class="operation-symbol">=</div>

                    <!-- Result Dimensions Preview -->
                    <div class="matrix-container">
                        <h3 class="matrix-title">Result ({{ rows_a }}×{{ cols_b }})</h3>
                        <div style="text-align: center; padding: 40px; color: rgba(255, 255, 255, 0.7); font-style: italic;">
                            Click calculate to see result
                        </div>
                    </div>
                </div>

                <button type="submit" name="submit_matrices" class="btn btn-center">
                    🚀 Calculate Matrix Multiplication
                </button>
            </form>
        </div>
        {% endif %}

        {% if result %}
        <!-- Step 3: Show Result -->
        <div class="result-section">
            <h2 class="result-title">✨ Matrix Multiplication Result ({{ rows_a }}×{{ cols_b }})</h2>
            <div class="result-matrix">
                <table class="result-table">
                    {% for row in result %}
                        <tr>
                        {% for val in row %}
                            <td>{{ "%.2f"|format(val) if val != val|int else val|int }}</td>
                        {% endfor %}
                        </tr>
                    {% endfor %}
                </table>
            </div>
            <br>
            <a href="/" class="reset-btn">🔄 Calculate Another Multiplication</a>
        </div>
        {% endif %}

        {% if error %}
        <div class="error-message">
            ❌ {{ error }}
        </div>
        {% endif %}
    </div>
</body>
</html>

@app.route('/')
def index():
    return render_template_string(HTML_STYLE + '''
    <div class="floating-shapes">
        <div class="shape"></div>
        <div class="shape"></div>
        <div class="shape"></div>
    </div>
    <div class="container">
        <div class="icon">🚀</div>
        <h2>Welcome Back</h2>
        <p style="text-align: center; color: rgba(255,255,255,0.8); margin-bottom: 30px;">
            Manage your account with style
        </p>
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">🔐</div>
                <div>Secure</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">⚡</div>
                <div>Fast</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">🎯</div>
                <div>Simple</div>
            </div>
        </div>
        <div class="home-buttons">
            <a href="/register">
                <button type="button">📝 Create New Account</button>
            </a>
            <a href="/login">
                <button type="button">🔑 Login to Account</button>
            </a>
            <a href="/init-db">
                <button type="button" style="background: linear-gradient(135deg, rgba(255, 206, 84, 0.2) 0%, rgba(255, 107, 107, 0.2) 100%);">
                    🔄 Reset Database
                </button>
            </a>
        </div>
    </div>
    ''')

@app.route('/register')
def register_page():
    return render_template_string(HTML_STYLE + '''
    <div class="floating-shapes">
        <div class="shape"></div>
        <div class="shape"></div>
        <div class="shape"></div>
    </div>
    <div class="container">
        <div class="icon">✨</div>
        <h2>Create Account</h2>
        <form method="POST" action="/register">
            <div class="form-group">
                <input type="text" name="username" placeholder="Username (required)" required minlength="3">
            </div>
            <div class="form-group">
                <input type="email" name="email" placeholder="Email (optional)">
            </div>
            <div class="form-group">
                <input type="text" name="full_name" placeholder="Full Name (optional)">
            </div>
            <div class="form-group">
                <input type="text" name="phone" placeholder="Phone (optional)">
            </div>
            <div class="form-group">
                <input type="password" name="password" placeholder="Password (min 6 chars)" required minlength="6">
            </div>
            <div class="form-group">
                <input type="password" name="confirm_password" placeholder="Confirm Password" required>
            </div>
            <button type="submit">Create Account</button>
        </form>
        <div class="link">
            <a href="/login">Already have an account? Login here</a>
        </div>
        <div class="link">
            <a href="/">← Back to Home</a>
        </div>
    </div>
    ''')

@app.route('/login')
def login_page():
    return render_template_string(HTML_STYLE + '''
    <div class="floating-shapes">
        <div class="shape"></div>
        <div class="shape"></div>
        <div class="shape"></div>
    </div>
    <div class="container">
        <div class="icon">🔮</div>
        <h2>Welcome Back</h2>
        <form method="POST" action="/login">
            <div class="form-group">
                <input type="text" name="username" placeholder="Enter Username" required>
            </div>
            <div class="form-group">
                <input type="password" name="password" placeholder="Enter Password" required>
            </div>
            <button type="submit">Login</button>
        </form>
        <div class="link">
            <a href="/register">Need an account? Register here</a>
        </div>
        <div class="link">
            <a href="/">← Back to Home</a>
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
    <div class="floating-shapes">
        <div class="shape"></div>
        <div class="shape"></div>
        <div class="shape"></div>
    </div>
    <div class="container">
        <div class="icon">🎯</div>
        <h2>Dashboard</h2>
        <div class="message success">
            <h3>Welcome, {}!</h3>
            <p>You are successfully logged in to your dashboard.</p>
        </div>
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">✅</div>
                <div>Active</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">🔐</div>
                <div>Secure</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">🚀</div>
                <div>Ready</div>
            </div>
        </div>
        <div class="home-buttons">
            <a href="/logout">
                <button type="button" style="background: linear-gradient(135deg, rgba(255, 107, 107, 0.2) 0%, rgba(255, 142, 83, 0.2) 100%);">
                    🚪 Logout
                </button>
            </a>
            <a href="/">
                <button type="button">🏠 Home</button>
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
    <div class="container">
        <div class="message success">
            <div class="icon">🎉</div>
            <h3>Success!</h3>
            <p>{}</p>
        </div>
        <div class="link">
            <a href="{}"><button type="button">{}</button></a>
        </div>
    </div>
    '''.format(message, link_url, link_text))

def show_error(message):
    return render_template_string(HTML_STYLE + '''
    <div class="container">
        <div class="message error">
            <div class="icon">❌</div>
            <h3>Error</h3>
            <p>{}</p>
        </div>
        <div class="link">
            <a href="javascript:history.back()"><button type="button">Try Again</button></a>
        </div>
        <div class="link">
            <a href="/">Go Home</a>
        </div>
    </div>
    '''.format(message))

if __name__ == '__main__':
    print("Starting Flask application...")
    print("To reset database, visit: /init-db")
    print("To test database, visit: /test-db")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)