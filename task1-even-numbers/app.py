from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    even_numbers = []
    if request.method == 'POST':
        try:
            n = int(request.form['number'])
            even_numbers = [i for i in range(2, 2*n + 1, 2)]
        except:
            even_numbers = ['Invalid Input!']
    return render_template('index.html', even_numbers=even_numbers)

if __name__ == '__main__':
    app.run(debug=True)
