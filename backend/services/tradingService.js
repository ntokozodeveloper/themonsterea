const WebSocket = require('ws');
const config = require('../config/config');

exports.placeOrder = (symbol, amount, contract_type, callback) => {
    const ws = new WebSocket(config.DERIV_API_URL);

    ws.on('open', () => {
        // Send a request to create a new contract (order)
        // Removed Contract Type,  "contract_type": contract_type,  (Under basis)
        const orderRequest = {
            "buy": 1,
            "price": amount,
            "parameters": {
                "amount": amount,
                "basis": "payout",
                "contract_type": contract_type,
                "deriv_api_token": deriv_api_token,
                "token": deriv_api_token,
                "currency": "USD",
                "duration": 1,
                "duration_unit": "m",
                "symbol": symbol
            },
            "proposal": 1
        };
        ws.send(JSON.stringify(orderRequest));
    });

    ws.on('message', (data) => {
        const response = JSON.parse(data);
        if (response.error) {
            callback(response.error, null);
        } else if (response.buy) {
            callback(null, response);
        }
        ws.close();
    });

    ws.on('error', (error) => {
        callback(error, null);
    });
};

