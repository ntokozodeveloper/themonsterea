import requests
import json

# Define your IQ Option and Deriv API credentials
IQ_OPTION_API_TOKEN = "your_iq_option_api_token"
DERIV_API_TOKEN = "CgSoT3CZ2GFjviT"

# Define the Forex pair and timeframe for historical data retrieval
FOREX_PAIR = "EURUSD"
SYMBOL = "R_50" 
TIMEFRAME = "1m"  # 1 minute timeframe

# Define the API endpoints
IQ_OPTION_API_URL = f"https://api.iqoption.com/v1/candles?active_id={FOREX_PAIR}&size={TIMEFRAME}&from=0"
DERIV_API_URL = f"https://trade.deriv.com/api/quotes/history?symbol={SYMBOL}&adjust_start_time=0&count=100&granularity={TIMEFRAME}"

# Function to retrieve historical price data from IQ Option API
def get_iq_option_data():
    response = requests.get(IQ_OPTION_API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve data from IQ Option API.")
        return None

# Function to retrieve historical price data from Deriv API for Crash 500
def get_deriv_data():
    headers = {"Authorization": f"Bearer {DERIV_API_TOKEN}"}
    response = requests.get(DERIV_API_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve data from Deriv API.")
        return None

# Main function to fetch data from IQ Option API and print the results
def main_iq_option():
    iq_option_data = get_iq_option_data()

    if iq_option_data:
        print("Historical price data from IQ Option:")
        print(json.dumps(iq_option_data, indent=4))

# Main function to fetch data from Deriv API for Crash 500 and print the results
def main_deriv():
    deriv_data = get_deriv_data()

    if deriv_data:
        print("Historical price data for Crash 500:")
        print(json.dumps(deriv_data, indent=4))

if __name__ == "__main__":
    main_iq_option()  # Fetch data from IQ Option API
    main_deriv()      # Fetch data from Deriv API for Crash 500