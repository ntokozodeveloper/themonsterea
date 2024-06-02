const tradingService = require('../services/tradingService');

exports.executeTrade = (req, res) => {
    const { symbol, amount, deriv_api_token, contract_type } = req.body;  // Ensure your request includes these parameters, 
    tradingService.placeOrder(symbol, amount, deriv_api_token, contract_type, (error, result) => {
        if (error) {
            res.status(500).send(`Error: ${error}`);
        } else {
            res.send(result);
        }
    });
};


///  contract_type,