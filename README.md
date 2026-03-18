# Binance Futures Testnet Trading Bot

Small Python CLI application for placing `MARKET` and `LIMIT` orders on Binance USDT-M Futures Testnet with reusable structure, validation, logging, and error handling.

## Features

- Places `MARKET` and `LIMIT` orders on Binance Futures Testnet
- Supports both `BUY` and `SELL`
- Validates CLI input before making API calls
- Separates CLI, validation, API client, and order service layers
- Logs requests, responses, and errors to a file
- Handles invalid input, missing credentials, API errors, and network failures

## Project Structure

```text
trading bot/
  bot/
    __init__.py
    client.py
    exceptions.py
    logging_config.py
    orders.py
    validators.py
  cli.py
  README.md
  requirements.txt
  logs/
```

## Setup

1. Create and activate a Python 3 virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

2.1 (Windows) If `requests` is missing:

```powershell
python -m pip install -r requirements.txt
```

3. Create Binance Futures Testnet API credentials at:

```text
https://testnet.binancefuture.com
```

4. Set environment variables (PowerShell):

```powershell
$env:BINANCE_API_KEY="your_testnet_api_key"
$env:BINANCE_API_SECRET="your_testnet_api_secret"
```

or (cmd.exe):

```cmd
setx BINANCE_API_KEY "your_testnet_api_key"
setx BINANCE_API_SECRET "your_testnet_api_secret"
```

## Usage

### MARKET order

```bash
python cli.py --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001
```

### LIMIT order

```bash
python cli.py --symbol BTCUSDT --side SELL --order-type LIMIT --quantity 0.001 --price 120000
```

## Example Output

```text
Order Request Summary
  Symbol: BTCUSDT
  Side: BUY
  Type: MARKET
  Quantity: 0.001
  Price: N/A
Order Response Details
  Order ID: 123456789
  Status: FILLED
  Executed Quantity: 0.001
  Average Price: 67250.1
Success: order placed successfully.
```

## Logging

- Log file path: `logs/trading_bot.log`
- Logs include request metadata, response payloads, and failure details

## Assumptions

- Orders are placed against Binance USDT-M Futures Testnet only
- API key and secret are supplied through environment variables
- Symbol precision, price tick size, and account-level trading restrictions are enforced by Binance; this app surfaces Binance validation errors directly

## Notes for Submission

- Run one `MARKET` order and one `LIMIT` order using your own testnet credentials
- Include the generated log file(s) from those runs in the repository or zip submission
- If you want separate logs per run, rename `logs/trading_bot.log` after each command

