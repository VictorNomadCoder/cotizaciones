import yfinance as yf
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/cotizacion', methods=['GET'])
def obtener_cotizacion():
    ticker = request.args.get('ticker', '')
    if not ticker:
        return jsonify({"error": "Debes proporcionar un ticker"}), 400
    
    try:
        etf = yf.Ticker(ticker)
        hist = etf.history(period="1d")
        if hist.empty:
            return jsonify({"error": "No se encontró el ticker"}), 404
        
        precio = hist["Close"].iloc[-1]
        return jsonify({"ticker": ticker, "precio": precio})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
