const express = require('express');
const bodyParser = require('body-parser');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const http = require('http');
const { Server } = require('socket.io');
const axios = require('axios');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

// Use Helmet to help secure your app with various HTTP headers
app.use(helmet());

// Body parser middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Rate limiting to prevent abuse
const apiLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // Limit each IP to 100 requests per windowMs
});
app.use('/api/', apiLimiter);

// List of valid serial keys
const validSerialKeys = [
    'S44V-Y6MD-EUXN-NCFO-63IQ92ISY5-SE-H4A19-CAXWRI-I-VH8',
    'Z7C8-WCYZ-OMRP-NSZJ-5FAXWAH2VH-MU-OZBRP-T4AH8Q-N-YQQ',
    'CV8U-V5XV-NR9Q-3K5I-4EFHSG89XM-4Q-BFFCO-TO2AQU-0-R0X',
    'CBQU-H286-FICJ-NLNN-RYX379YF0A-1H-J9V0A-LG5AIJ-I-GLP',
    '11WQ-HOJQ-48SS-VX5Q-BETKM7N8ZR-RN-KO488-FQP05A-9-SPK',
    'QJ7F-A49B-I4J1-Y25S-UDBGUVDFAV-WS-0JIH1-5QZ8HZ-E-8WC',
    '4W3M-0NYS-Z1QC-EWJN-ARXIQBNSFR-IY-OY0L5-JT6116-8-VGT',
    'N2CH-X7NT-7ZTY-7VII-FPPH4ZL9R2-DV-7RMTO-2K6IHY-7-AYF',
    'PCVQ-U23K-38FY-307F-8NJ5WNF2H3-TZ-2W6WN-P9H9SQ-J-8OF',
    'GAO6-PGTZ-C9IE-GVYH-T8TDD1WXRP-VF-0PBZH-G2KX3I-Q-Z2O',
    '3KHB-KLOS-A3FK-G2JC-M0WC4RTLXL-01-5OMXZ-7VGFW1-D-TEZ',
    '7VGO-TSUM-B9M9-N36U-O6NFZT48ON-TY-2917C-V3A6S8-K-VPX',
    'Nomafu'
    // Add more keys as needed
];

// Serve the HTML form
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Handle form submission with serial key validation
app.post('/trade', async (req, res) => {
    const { serialKey, symbol, amount, contract_type } = req.body;

    // Validate the serial key
    if (!validSerialKeys.includes(serialKey)) {
        return res.status(401).json({ errors: 'Invalid serial key.' });
    }

    // Validate the form data
    if (!symbol || !amount || !contract_type) {
        return res.status(400).json({ errors: 'All fields are required.' });
    }

    try {
        // Send the data to the Python backend
        const response = await axios.post('http://localhost:5000/api/trade', {
            symbol,
            amount,
            contract_type
        });

        // Emit trade update to all connected clients
        io.emit('tradeUpdate', response.data);

        res.json(response.data);
    } catch (error) {
        res.status(500).json({ errors: error.message });
    }
});

// Error handling for undefined routes
app.use((req, res, next) => {
    res.status(404).send('Not Found');
});

// Global error handler
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).send('Something broke!');
});

// Socket.io connection handling
io.on('connection', (socket) => {
    console.log('New client connected');
    socket.on('disconnect', () => {
        console.log('Client disconnected');
    });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
