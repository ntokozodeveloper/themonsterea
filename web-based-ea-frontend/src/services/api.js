const API_URL = 'http://localhost:3000';

export async function getHistoricalData() {
    const response = await fetch(`${API_URL}/analyze/historical-data`);
    return response.json();
}

export async function executeTrade(tradeDetails) {
    const response = await fetch(`${API_URL}/trade/execute`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(tradeDetails),
    });
    return response.json();
}
