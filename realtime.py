from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import numpy as np
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)

def calculate_probability(sma_50, sma_200):
    """Calculate the probability based on SMA distances."""
    distance = abs(sma_50 - sma_200)
    max_distance = max(sma_50, sma_200)
    probability = (distance / max_distance) * 100
    return round(probability, 2)

def recommend_lot_size(probability, account_balance):
    """Recommend lot size based on probability and account balance."""
    risk_per_trade = 0.01  # 1% of the account balance
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


def download_data(ticker_symbol, interval, start_date, end_date):
    logging.info(f"Downloading data for {ticker_symbol} from {start_date} to {end_date} with interval {interval}")
    try:
        data = yf.download(ticker_symbol, start=start_date, end=end_date, interval=interval)
        if data.empty:
            logging.info(f"No data available for {ticker_symbol} at interval {interval}")
            return None
        logging.info(f"Successfully downloaded data for {ticker_symbol} at interval {interval}")
        return data
    except Exception as e:
        logging.error(f"Error downloading data for {ticker_symbol} at interval {interval}: {e}")
        return None


def process_data(data_frames):
    """Calculate SMAs and generate trade signals."""
    signals = {}
    
    for interval, data in data_frames.items():
        logging.info(f"Processing data for interval {interval}")
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['SMA_200'] = data['Close'].rolling(window=200).mean()
        data['Signal'] = np.where(data['SMA_50'] > data['SMA_200'], 1, 0)
        data['Position'] = data['Signal'].diff()
        signals[interval] = data.iloc[-1] if not data.empty else None
        logging.info(f"Processed data for interval {interval}: {signals[interval]}")
        
    return signals

def generate_trade_signals(signals):
    logging.info("Generating trade signals")
    
    # Try preferred timeframes first
    for interval in ['30m', '1h']:
        if signals.get(interval) is not None:
            recent_signal = signals[interval]
            trade_signal = 'buy' if recent_signal['Signal'] == 1 else 'sell'
            entry_price = recent_signal['Close']
            probability = calculate_probability(recent_signal['SMA_50'], recent_signal['SMA_200'])
            logging.info(f"Trade signal: {trade_signal} for interval {interval}")
            return trade_signal, entry_price, probability, interval

    # Check daily timeframe if no signal found in preferred timeframes
    if signals.get('1d') is not None:
        recent_signal = signals['1d']
        trade_signal = 'buy' if recent_signal['Signal'] == 1 else 'sell'
        entry_price = recent_signal['Close']
        probability = calculate_probability(recent_signal['SMA_50'], recent_signal['SMA_200'])
        logging.info(f"Trade signal: {trade_signal} for daily interval")
        return trade_signal, entry_price, probability, '1d'

    logging.info("No trade signal generated")
    return 'hold', None, 0, 'No signal'


@app.route('/api/trade', methods=['POST'])
def trade():
    data = request.json

    symbol = data.get('symbol')
    amount = data.get('amount')
    contract_type = data.get('contract_type')
    deriv_api_token = data.get('deriv_api_token')
    stop_loss_percent = data.get('stop_loss_percent', 1)  # default 1% stop loss
    take_profit_percent = data.get('take_profit_percent', 2)  # default 2% take profit

    if not symbol or not amount or not contract_type:
        return jsonify({'errors': 'Invalid input'}), 400

    # Adjust ticker symbol format for Yahoo Finance
    if symbol == 'USDZAR':
        ticker_symbol ='USDZAR=X'
    if symbol == 'GBPJPY':
        ticker_symbol = 'GBPJPY=X'
    elif symbol == 'EURUSD':
        ticker_symbol = 'EURUSD=X'
    elif symbol == 'USDJPY':
        ticker_symbol = 'USDJPY=X'
    elif symbol == 'AUDUSD':
        ticker_symbol = 'AUDUSD=X'
    elif symbol == 'USDCAD':
        ticker_symbol = 'USDCAD=X'
    elif symbol == 'USDCHF':
        ticker_symbol = 'USDCHF=X'
    elif symbol == 'EURJPY':
        ticker_symbol = 'EURJPY=X'
    elif symbol == 'GBPJPY':
        ticker_symbol = 'GBPJPY=X'
    elif symbol == 'AUDJPY':
        ticker_symbol = 'AUDJPY=X'
    elif symbol == 'EURGBP':
        ticker_symbol = 'EURGBP=X'
    elif symbol == 'EURCHF':
        ticker_symbol = 'EURCHF=X'
    elif symbol == 'EURAUD':
        ticker_symbol = 'EURAUD=X'
    else:
        ticker_symbol = f'{symbol}=X'  # Default case

    start_date = '2020-01-01'
    end_date = '2026-05-29'

    intervals = ['3mo', '1mo', '1wk', '1d', '1h', '30m']
    data_frames = {interval: download_data(ticker_symbol, interval, start_date, end_date) for interval in intervals}

    # Filter out None values
    data_frames = {k: v for k, v in data_frames.items() if v is not None}

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
    app.run(port=5000)
