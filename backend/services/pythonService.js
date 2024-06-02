const { exec } = require('child_process');

exports.runPythonScript = (scriptPath, callback) => {
    exec(`python ${scriptPath}`, (error, stdout, stderr) => {
        if (error) {
            callback(`exec error: ${error}`, null);
            return;
        }
        callback(null, stdout);
    });
};
