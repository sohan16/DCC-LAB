from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    n = None
    if request.method == 'POST':
        numbers_str = request.form['numbers']
        n = int(request.form['n'])
        try:
            numbers = [int(num.strip()) for num in numbers_str.split(',')]
            if 1 <= n <= len(numbers):
                numbers.sort(reverse=True)
                result = numbers[n - 1]
            else:
                result = "Invalid value of n"
        except ValueError:
            result = "Please enter only numbers separated by commas."
    return render_template('index.html', result=result, n=n)
