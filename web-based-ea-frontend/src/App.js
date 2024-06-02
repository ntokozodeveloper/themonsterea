import React, { useState, useEffect } from 'react';
import { getHistoricalData, executeTrade } from './services/api';
import io from 'socket.io-client';

function App() {
    const [data, setData] = useState(null);
    const [tradeResult, setTradeResult] = useState(null);

    useEffect(() => {
        async function fetchData() {
            const result = await getHistoricalData();
            setData(result);
        }
        fetchData();
    }, []);

    const handleTrade = async () => {
        const result = await executeTrade({ /* your trade details here */ });
        setTradeResult(result);
    };

    return (
        <div>
            <h1>Historical Data</h1>
            <pre>{JSON.stringify(data, null, 2)}</pre>
            <button onClick={handleTrade}>Execute Trade</button>
            {tradeResult && (
                <div>
                    <h2>Trade Result</h2>
                    <pre>{JSON.stringify(tradeResult, null, 2)}</pre>
                </div>
            )}
        </div>
    );
}

//**Socket, Real time updates */

const socket = io('http://localhost:3000');

function App() {
  const [tradeData, setTradeData] = useState([]);

  useEffect(() => {
    socket.on('tradeUpdate', (data) => {
      setTradeData((prevData) => [...prevData, data]);
    });

    return () => {
      socket.off('tradeUpdate');
    };
  }, []);

  return (
    <div>
      <h1>Trade Data</h1>
      <ul>
        {tradeData.map((trade, index) => (
          <li key={index}>{JSON.stringify(trade)}</li>
        ))}
      </ul>
    </div>
  );
}


export default App;

