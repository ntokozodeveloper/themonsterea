const express = require('express');
const router = express.Router();
const tradeController = require('../controllers/tradeController');

router.post('/', tradeController.executeTrade);

module.exports = router;
