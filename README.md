# The Monster Expert Advisor

Welcome to The Monster Expert Advisor (EA) project! This open-source EA is designed to provide reliable and easy-to-use automated trading solutions for Forex traders. The Monster EA leverages cutting-edge technologies to analyze market data, execute trades, and handle user inputs securely.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Introduction

The Monster Expert Advisor is an open-source project aimed at developing a robust and user-friendly trading bot for the Forex market. Our goal is to create a reliable EA that can be used by traders worldwide, regardless of their location or experience level. 

## Features

- **Automated Trading**: Executes trades automatically based on pre-defined strategies.
- **Secure User Inputs**: Handles account numbers, passwords, and API keys securely.
- **Market Analysis**: Analyzes market trends and data to make informed trading decisions.
- **Cross-Platform Compatibility**: Works with MetaTrader 4 and MetaTrader 5 on any broker that supports Expert Advisors.

## Technologies Used

The Monster Expert Advisor is built on the following technologies:

- **Node.js**: Backend server for executing trades, analyzing the market, and handling user inputs.
- **React.js**: Frontend interface for user interaction and data visualization.
- **Python**: Fetches historical market data, calculates trade probabilities, recommends lot sizes, and generates signals.

## Installation

To get started with The Monster Expert Advisor, follow these steps:

1. Clone the repository:
    ```bash
    git clone (https://github.com/ntokozodeveloper/themonsterea.git
    ```
2. Navigate to the project directory:
    ```bash
    cd themonsterea
    ```
3. Install dependencies for the backend:
    ```bash
    cd backend
    npm install
    ```
4. Install dependencies for the frontend:
    ```bash
    cd ../frontend
    npm install
    ```
5. Set up the Python environment and install necessary packages:
    ```bash
    cd ../python
    pip install -r requirements.txt
    ```
6. Note: web-based-ea
This folder contains the source code for the Monster Expert Advisor. When starting the backend and frontend, you don't need to navigate to each directory separately. Instead, you can start the server in the "web-based-ea" directory by running the command "npm start," which will concurrently start both the backend and frontend.

## Usage

1. Start the server:
    ```bash
    cd web-based-ea
    npm start
    ```
2. Run the Python scripts for data fetching and analysis:
    ```bash
    python realtime.py
    ```
The Python script will start Flask on port 5000. You can access the server at "localhost:3000" once you have started the server and run the Python command mentioned above. So, open two terminals: one for the server and one for the Python script. Have fun coding!
## Contributing

We welcome contributions from developers around the world. To contribute to The Monster Expert Advisor, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
    ```bash
    git checkout -b feature-name
    ```
3. Commit your changes.
    ```bash
    git commit -m "Description of your feature"
    ```
4. Push to the branch.
    ```bash
    git push origin feature-name
    ```
5. Open a pull request and describe your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions, suggestions, or feedback, please reach out to me via email at [b2ntokozo@gmail.com](mailto:b2ntokozo@gmail.com).

Thank you for being a part of The Monster Expert Advisor project!
