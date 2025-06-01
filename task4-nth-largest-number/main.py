from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/nth-largest', methods=['GET'])
def nth_largest():
    numbers_str = request.args.get('numbers')
    n = request.args.get('n')

    if not numbers_str or not n:
        return jsonify({'error': 'Please provide both numbers and n'}), 400

    try:
        numbers = list(map(int, numbers_str.split(',')))
        n = int(n)

        if n <= 0 or n > len(numbers):
            return jsonify({'error': 'Invalid value of n'}), 400

        nth_largest_number = sorted(numbers, reverse=True)[n - 1]
        return jsonify({'nth_largest': nth_largest_number})
    except ValueError:
        return jsonify({'error': 'Invalid input'}), 400

if __name__ == '__main__':
    app.run(debug=True)
