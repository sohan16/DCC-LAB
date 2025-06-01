from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    numbers_input = ''
    n_input = ''
    
    if request.method == 'POST':
        numbers_input = request.form['numbers']
        n_input = request.form['n']
        
        try:
            number_list = [int(x.strip()) for x in numbers_input.split(',')]
            number_list.sort(reverse=True)

            n = int(n_input)
            if n <= len(number_list):
                result = f"The {n}th largest number is: {number_list[n-1]}"
            else:
                result = f"Error: N is greater than the size of the list."
        except ValueError:
            result = "Please enter valid integers separated by commas."
    
    return render_template('index.html', result=result, numbers_input=numbers_input, n_input=n_input)

if __name__ == '__main__':
    app.run(debug=True)
