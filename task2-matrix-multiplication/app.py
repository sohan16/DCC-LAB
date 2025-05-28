from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    rows_a = None
    cols_a = None
    rows_b = None
    cols_b = None
    
    if request.method == 'POST':
        if 'submit_dimensions' in request.form:
            # Step 1: user submitted matrix dimensions
            try:
                rows_a = int(request.form['rows_a'])
                cols_a = int(request.form['cols_a'])
                rows_b = int(request.form['rows_b'])
                cols_b = int(request.form['cols_b'])
                
                # Validation for matrix multiplication rule
                if rows_a < 1 or cols_a < 1 or rows_b < 1 or cols_b < 1:
                    error = "All dimensions must be at least 1."
                elif cols_a != rows_b:
                    error = f"Matrix multiplication not possible! Columns of Matrix A ({cols_a}) must equal Rows of Matrix B ({rows_b})."
                    rows_a = cols_a = rows_b = cols_b = None
                    
            except ValueError:
                error = "Please enter valid numbers for dimensions."
                
        elif 'submit_matrices' in request.form:
            # Step 2: user submitted the matrix elements for multiplication
            try:
                rows_a = int(request.form['rows_a'])
                cols_a = int(request.form['cols_a'])
                rows_b = int(request.form['rows_b'])
                cols_b = int(request.form['cols_b'])
                
                # Read Matrix A
                matrix_a = []
                for i in range(rows_a):
                    row = []
                    for j in range(cols_a):
                        value = request.form.get(f'a{i}{j}', '0')
                        try:
                            row.append(float(value))
                        except ValueError:
                            row.append(0)
                    matrix_a.append(row)
                
                # Read Matrix B
                matrix_b = []
                for i in range(rows_b):
                    row = []
                    for j in range(cols_b):
                        value = request.form.get(f'b{i}{j}', '0')
                        try:
                            row.append(float(value))
                        except ValueError:
                            row.append(0)
                    matrix_b.append(row)
                
                # Matrix multiplication: A(m×n) × B(n×p) = C(m×p)
                result = []
                for i in range(rows_a):  # rows of result = rows of A
                    row = []
                    for j in range(cols_b):  # cols of result = cols of B
                        sum_val = 0
                        for k in range(cols_a):  # or range(rows_b) - they're equal
                            sum_val += matrix_a[i][k] * matrix_b[k][j]
                        row.append(sum_val)
                    result.append(row)
                    
            except Exception as e:
                error = f"Error in matrix multiplication: {str(e)}"
    
    return render_template('index.html', 
                         rows_a=rows_a, cols_a=cols_a, 
                         rows_b=rows_b, cols_b=cols_b, 
                         result=result, error=error)

if __name__ == '__main__':
    app.run(debug=True)