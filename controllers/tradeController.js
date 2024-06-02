const tradingService = require('../services/tradingService');

exports.executeTrade = (req, res) => {
    const { symbol, amount, contract_type } = req.body;  // Ensure your request includes these parameters
    tradingService.placeOrder(symbol, amount, contract_type, (error, result) => {
        if (error) {
            res.status(500).send(`Error: ${error}`);
        } else {
            res.send(result);
        }
    });
};
