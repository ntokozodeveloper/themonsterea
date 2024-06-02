const pythonService = require('../services/pythonService');

exports.analyzeData = (req, res) => {
    pythonService.runPythonScript('../realtime.py', (error, result) => {
        if (error) {
            res.status(500).send(`Error: ${error}`);
        } else {
            res.send(result);
        }
    });
};
