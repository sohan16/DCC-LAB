
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

HTML_STYLE = """<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
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
        animation: fadeIn 0.5s ease-in;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .header {
        text-align: center;
        margin-bottom: 25px;
    }
    .header h2 {
        color: #222;
        font-size: 26px;
    }
    .header p {
        color: #666;
        font-size: 14px;
    }
    .form-group {
        margin-bottom: 20px;
    }
    .form-group label {
        color: #333;
        font-weight: 500;
        margin-bottom: 6px;
        display: block;
    }
    .form-group input {
        width: 100%;
        padding: 12px;
        border: 1.8px solid #ddd;
        border-radius:  10px;
        font-size: 15px;
        transition: 0.3s;
    }
    .form-group input:focus {
        border-color: #66a6ff;
        outline: none;
        box-shadow: 0 0 0 3px rgba(102,166,255,0.2);
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
        transition: 0.3s;
    }
    .btn:hover {
        background: #445ef7;
        box-shadow: 0 6px 15px rgba(102,166,255,0.4);
    }
    .message {
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 15px;
    }
    .success {
        background: #e6f9f0;
        color: #2e7d32;
        border: 1px solid #b2dfdb;
    }
    .error {
        background: #fdecea;
        color: #c62828;
        border: 1px solid #f5c6cb;
    }
    .warning {
        background: #fff8e1;
        color: #ef6c00;
        border: 1px solid #ffe082;
    }
    .links {
        margin-top: 20px;
        text-align: center;
    }
    .links a {
        color: #1976d2;
        text-decoration: none;
        font-weight: 500;
    }
    .links a:hover {
        text-decoration: underline;
    }
</style>"""

@app.route('/')
def home():
    return render_template_string(HTML_STYLE + "<div class='container'><h2 class='header'>Welcome!</h2></div>")

if __name__ == '__main__':
    app.run(debug=True)
