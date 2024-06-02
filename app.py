from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route('/api/trade', methods=['POST'])
def trade():
    data = request.json

    symbol = data.get('symbol')
    amount = data.get('amount')
    contract_type = data.get('contract_type')

    if not symbol or not amount or not contract_type:
        return jsonify({'errors': 'Invalid input'}), 400

    # Trading logic based on historical data
    ticker_symbol = f'{symbol}=X' if symbol.endswith('USD') else symbol
    start_date = '2020-01-01'
    end_date = '2025-05-29'

    ticker = yf.Ticker(ticker_symbol)
    historical_data = ticker.history(start=start_date, end=end_date, interval='1d')

    historical_data['SMA_50'] = historical_data['Close'].rolling(window=50).mean()
    historical_data['SMA_200'] = historical_data['Close'].rolling(window=200).mean()
    historical_data['Signal'] = 0
    historical_data['Signal'][50:] = (historical_data['SMA_50'][50:] > historical_data['SMA_200'][50:]).astype(int)
    historical_data['Position'] = historical_data['Signal'].diff()

    signal_changes = historical_data[historical_data['Position'] != 0]
    recent_signal = signal_changes.iloc[-1] if not signal_changes.empty else None

    if recent_signal is not None:
        trade_signal = 'buy' if recent_signal['Signal'] == 1 else 'sell'
    else:
        trade_signal = 'hold'

    result = {
        'status': 'success',
        'message': f'Trade signal: {trade_signal}',
        'recent_signal': recent_signal.to_dict() if recent_signal is not None else None,
        'data': data
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000)