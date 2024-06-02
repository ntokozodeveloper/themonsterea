const express = require('express');
const router = express.Router();
const axios = require('axios');
const { check, validationResult } = require('express-validator');

// Define a route to handle trade requests
router.post('/',
    // Validate and sanitize inputs
    [
        check('symbol').isString().trim().notEmpty(),
        check('amount').isNumeric(),
        check('deriv_api_token').isString().trim().notEmpty()
    ],
    async (req, res) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({ errors: errors.array() });
        }

        try {
            const response = await axios.post('http://localhost:5000/api/trade', req.body);
            res.status(200).json(response.data);
        } catch (error) {
            res.status(500).json({ message: error.message });
        }
    }
);

module.exports = router;
