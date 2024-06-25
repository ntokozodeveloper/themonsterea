const PORT = process.env.PORT || 3000;

const express = require("express");
const bodyParser = require("body-parser");
const analyzeRoutes = require("./routes/analyze");
const tradeRoutes = require("./routes/trade");
const app = express();

app.use(bodyParser.json());

// Add a route handler for the root URL
app.get("/", (req, res) => {
  res.send("Welcome to the Trading API");
});

app.use("/analyze", analyzeRoutes);
app.use("/trade", tradeRoutes);

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
