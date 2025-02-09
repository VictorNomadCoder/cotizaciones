import yfinance as yf
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# API para obtener el tipo de cambio USD a EUR
def obtener_tipo_de_cambio():
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        data = response.json()
        return data["rates"]["EUR"]
    except Exception as e:
        return None  # En caso de error, devolverá None y evitará que falle la app

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
        
        precio_usd = hist["Close"].iloc[-1]  # Precio en USD
        
        # Obtener tipo de cambio y convertir a EUR
        tipo_de_cambio = obtener_tipo_de_cambio()
        if tipo_de_cambio is None:
            return jsonify({"error": "No se pudo obtener el tipo de cambio"}), 500
        
        precio_eur = precio_usd * tipo_de_cambio  # Convertir a EUR
        
        return jsonify({
            "ticker": ticker,
            "precio_usd": precio_usd,
            "precio_eur": precio_eur
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
