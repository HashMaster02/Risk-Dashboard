from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})

# TODO: Data validation
@app.route("/alert", methods=["POST"])
def receive_data():
    data = request.get_json()
    ticker = data.get("ticker")
    price = data.get("price")

    print(f"ROUTE:/alert :: Ticker: {ticker}, Price: {price}")

    return jsonify({
        "ticker": ticker,
        "price": price,
        "message": "Data received successfully"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
