from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import yfinance as yf
import pandas as pd
import talib
import numpy as np
from ta import add_all_ta_features
from ta.utils import dropna
import logging
from datetime import datetime, timedelta
import asyncio
from deriv_api import DerivAPI

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Deriv Connection
async def initialize_deriv_api(app_id, api_token):
    try:
        api = DerivAPI(app_id=app_id, endpoint=f'wss://ws.derivws.com/websockets/v3?app_id={app_id}&auth_token={api_token}')
        await api.api_connect()
        logging.info("Successfully connected to DerivAPI")
        return api
    except Exception as e:
        logging.error(f"Failed to connect to DerivAPI: {e}")
        return None

async def fetch_deriv_data(api, symbol, interval, start_date, end_date):
    try:
        interval_mapping = {
            '1m': '1min',
            '5m': '5min',
            '15m': '15min',
            '30m': '30min',
            '1h': '1h',
            '1d': '1d',
            '1w': '1w',
            '1M': '1M'
        }
        deriv_interval = interval_mapping.get(interval, '1d')  # Default to '1d' if not found

        # Log the request details
        logging.debug(f"Fetching Deriv data for {symbol} with interval {interval} from {start_date} to {end_date}")

        ticks_history_request = {
            "ticks_history": symbol,
            "adjust_start_time": 1,
            "count": 1000,
            "start": 1,  # Use start date directly as a string
            "end": "latest",  # Use "latest" directly
            "style": "candles"
        }

        response = await api.send(ticks_history_request)
        if 'error' in response:
            logging.error(f"Error fetching Deriv data: {response['error']['message']}")
            return pd.DataFrame()
        
        if 'candles' not in response:
            logging.warning("Response does not contain 'candles' data.")
            return pd.DataFrame()

        data = response['candles']
        df = pd.DataFrame(data)

        # Ensure 'volume' field is present in the DataFrame
        if 'volume' not in df.columns:
            logging.warning("'volume' column is missing in the response data.")
            df['volume'] = 0  # Add a default volume column if missing
        
        df['timestamp'] = pd.to_datetime(df['epoch'], unit='s')
        df.set_index('timestamp', inplace=True)
        df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
        logging.info(f"Successfully fetched Deriv data for {symbol} with interval {interval}")
        return df[['Open', 'High', 'Low', 'Close', 'Volume']]
    except Exception as e:
        logging.error(f"Error fetching Deriv data: {e}")
        return pd.DataFrame()

def combine_data(yf_data, deriv_data):
    if yf_data is None or yf_data.empty:
        logging.warning("Yahoo Finance data is empty or not available. Using only Deriv data.")
        return deriv_data
    if deriv_data is None or deriv_data.empty:
        logging.warning("Deriv data is empty or not available. Using only Yahoo Finance data.")
        return yf_data

    combined_data = pd.concat([yf_data, deriv_data])
    combined_data = combined_data[~combined_data.index.duplicated(keep='first')]
    combined_data.sort_index(inplace=True)
    logging.info("Successfully combined data from Yahoo Finance and Deriv")
    return combined_data

def calculate_probability(atr, close_price):
    max_atr = close_price * 0.1
    probability = (atr / max_atr) * 100
    return round(probability, 2)

def recommend_lot_size(probability, account_balance):
    risk_per_trade = 0.01
    if probability >= 80:
        lot_size_factor = 0.02
    elif probability >= 60:
        lot_size_factor = 0.015
    elif probability >= 40:
        lot_size_factor = 0.01
    else:
        lot_size_factor = 0.005
    
    lot_size = account_balance * risk_per_trade * lot_size_factor
    return round(lot_size, 2)

def download_data(ticker_symbol, interval, start_date, end_date, retries=3):
    logging.info(f"Downloading data for {ticker_symbol} from {start_date} to {end_date} with interval {interval}")
    for attempt in range(retries):
        try:
            data = yf.download(ticker_symbol, start=start_date, end=end_date, interval=interval)
            if data.empty:
                logging.warning(f"No data available for {ticker_symbol} at interval {interval} on attempt {attempt + 1}")
                continue
            logging.info(f"Successfully downloaded data for {ticker_symbol} at interval {interval} on attempt {attempt + 1}")
            return data
        except Exception as e:
            logging.error(f"Error downloading data for {ticker_symbol} at interval {interval} on attempt {attempt + 1}: {e}")
    logging.error(f"Failed to download data for {ticker_symbol} after {retries} attempts")
    return None

def process_data(data_frames):
    signals = {}

    for interval, data in data_frames.items():
        logging.info(f"Processing data for interval {interval}")
        if data is None or data.empty:
            logging.warning(f"No data available for interval {interval}")
            continue

        data = dropna(data)
        if len(data) < 50:
            logging.warning(f"Not enough data for interval {interval}")
            continue

        # Add the technical indicators and signal logic here...
        data['EMA_50'] = talib.EMA(data['Close'], timeperiod=50)
        data['RSI'] = talib.RSI(data['Close'], timeperiod=14)
        data['MACD'], data['MACD_Signal'], data['MACD_Hist'] = talib.MACD(data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
        data['Upper_BB'], data['Middle_BB'], data['Lower_BB'] = talib.BBANDS(data['Close'], timeperiod=20)
        data['Stoch_K'], data['Stoch_D'] = talib.STOCH(data['High'], data['Low'], data['Close'], fastk_period=14, slowk_period=3, slowd_period=3)
        data['ATR'] = talib.ATR(data['High'], data['Low'], data['Close'], timeperiod=14)
        data['OBV'] = talib.OBV(data['Close'], data['Volume'])
        
        if len(data) >= 15:
            data = add_all_ta_features(data, open="Open", high="High", low="Low", close="Close", volume="Volume", fillna=True)
        
        conditions = [
            (data['EMA_50'] > data['Close']),
            (data['RSI'] < 30),
            (data['MACD_Hist'] > 0),
            (data['Close'] < data['Lower_BB']),
            (data['Stoch_K'] < data['Stoch_D']),
        ]
        
        data['Signal'] = np.where(np.all(conditions, axis=0), 1, 0)
        data['Position'] = data['Signal'].diff()
        signals[interval] = data.iloc[-1] if not data.empty else None
        logging.info(f"Processed data for interval {interval}: {signals[interval]}")

    return signals

def generate_trade_signals(signals):
    logging.info("Generating trade signals")

    for interval in ['30m', '1h']:
        if signals.get(interval) is not None:
            recent_signal = signals[interval]
            trade_signal = 'buy' if recent_signal['Signal'] == 1 else 'sell'
            entry_price = recent_signal['Close']
            probability = calculate_probability(recent_signal['ATR'], recent_signal['Close'])
            logging.info(f"Trade signal: {trade_signal} for interval {interval}")
            return trade_signal, entry_price, probability, interval

    if signals.get('1d') is not None:
        recent_signal = signals['1d']
        trade_signal = 'buy' if recent_signal['Signal'] == 1 else 'sell'
        entry_price = recent_signal['Close']
        probability = calculate_probability(recent_signal['ATR'], recent_signal['Close'])
        logging.info(f"Trade signal: {trade_signal} for daily interval")
        return trade_signal, entry_price, probability, '1d'

    logging.info("No trade signal generated")
    return 'hold', None, 0, 'No signal'

@app.route('/api/trade', methods=['POST'])
async def trade():
    logging.info("Received request at /api/trade")
    data = request.json

    symbol = data.get('symbol')
    amount = data.get('amount')
    contract_type = data.get('contract_type')
    app_id = data.get('app_id')
    api_token = data.get('api_token')
    stop_loss_percent = data.get('stop_loss_percent', 1)
    take_profit_percent = data.get('take_profit_percent', 2)

    if not symbol or not amount or not contract_type or not app_id or not api_token:
        return jsonify({'errors': 'Invalid input'}), 400

    ticker_symbol = f'{symbol}=X'
    start_date = '2020-01-01'
    end_date = '2026-05-29'

    intervals = ['3mo', '1mo', '1wk', '1d', '1h', '30m']
    data_frames = {}

    api = await initialize_deriv_api(app_id, api_token)
    if api is None:
        return jsonify({'errors': 'Failed to connect to DerivAPI'}), 500

    for interval in intervals:
        yf_data = download_data(ticker_symbol, interval, start_date, end_date)
        deriv_data = await fetch_deriv_data(api, symbol, interval, start_date, 'latest') if yf_data is None or len(yf_data) < 50 else None
        combined_data = combine_data(yf_data, deriv_data)
        if combined_data is not None and not combined_data.empty:
            data_frames[interval] = combined_data

    signals = process_data(data_frames)
    trade_signal, entry_price, probability, timeframe_displayed = generate_trade_signals(signals)

    if trade_signal != 'hold':
        stop_loss = entry_price * (1 - stop_loss_percent / 100) if trade_signal == 'buy' else entry_price * (1 + stop_loss_percent / 100)
        take_profit = entry_price * (1 + take_profit_percent / 100) if trade_signal == 'buy' else entry_price * (1 - take_profit_percent / 100)
    else:
        stop_loss = None
        take_profit = None

    lot_sizes = {f'Account Balance {balance}': recommend_lot_size(probability, balance) for balance in [100, 200, 500, 1000, 2000, 5000, 10000]}

    result = {
        'status': 'success',
        'message': f'Trade signal: {trade_signal}',
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'probability': f'{probability}%',
        'recommended_lot_sizes': lot_sizes,
        'timeframe_displayed': timeframe_displayed,
    }

    return jsonify(result)

if __name__ == '__main__':
    socketio.run(app, port=5000, debug=True)
