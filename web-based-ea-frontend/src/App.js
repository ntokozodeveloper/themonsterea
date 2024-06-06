import React, { useState, useEffect } from 'react';
import { getHistoricalData, executeTrade } from './services/api';
import io from 'socket.io-client';


//Deriv Connection
const WebSocket = require('ws');
const DerivAPI = require('@deriv/deriv-api/dist/DerivAPI');

const app_id = 61999; // Replace with your app_id or leave as 1089 for testing.
const websocket = new WebSocket(`wss://ws.derivws.com/websockets/v3?app_id=${app_id}`);
const api = new DerivAPI({ connection: websocket });
const basic = api.basic;
const ping_interval = 12000; // it's in milliseconds, which equals to 120 seconds
let interval;


basic.ping().then(console.log);

const newLocal = new WebSocket('wss://ws.derivws.com/websockets/v3?app_id=61999');

//Pass

// subscribe to `open` event
websocket.addEventListener('open', (event) => {
  console.log('websocket connection established: ', event);
  const sendMessage = JSON.stringify({ ping: 1 });
  websocket.send(sendMessage);

  // to Keep the connection alive
  interval = setInterval(() => {
    const sendMessage = JSON.stringify({ ping: 1 });
    websocket.send(sendMessage);
  }, ping_interval);
});

// subscribe to `message` event
websocket.addEventListener('message', (event) => {
  const receivedMessage = JSON.parse(event.data);
  console.log('new message received from server: ', receivedMessage);
});

// subscribe to `close` event
websocket.addEventListener('close', (event) => {
  console.log('websocket connectioned closed: ', event);
  clearInterval(interval);
});

// subscribe to `error` event
websocket.addEventListener('error', (event) => {
  console.log('an error happend in our websocket connection', event);
});

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

