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
    tickers = request.args.get('tickers', '')
    if not tickers:
        return jsonify({"error": "Debes proporcionar al menos un ticker"}), 400

    ticker_list = tickers.split(",")  # Convertir la cadena en una lista de tickers
    resultados = []

    tipo_de_cambio = obtener_tipo_de_cambio()
    if tipo_de_cambio is None:
        return jsonify({"error": "No se pudo obtener el tipo de cambio"}), 500

    for ticker in ticker_list:
        ticker = ticker.strip().upper()  # Eliminar espacios y convertir en mayúsculas
        try:
            etf = yf.Ticker(ticker)
            hist = etf.history(period="1d")

            if hist.empty:
                resultados.append(f"{ticker}: ERROR (No encontrado)")
                continue

            precio_usd = hist["Close"].iloc[-1]  # Precio en USD
            precio_eur = precio_usd * tipo_de_cambio  # Convertir a EUR

            resultados.append(f"{ticker}: {round(precio_usd, 2)} USD, {round(precio_eur, 2)} EUR")

        except Exception as e:
            resultados.append(f"{ticker}: ERROR ({str(e)})")

    return ", ".join(resultados)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
