const express = require('express');
const router = express.Router();
const analyzeController = require('../controllers/analyzeController');

router.get('/', analyzeController.analyzeData);

module.exports = router;
