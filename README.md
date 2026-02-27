Binance Futures Testnet Trading Bot
A Python CLI trading bot that places orders on Binance Futures Testnet (USDT-M). Built with clean separation between the API client, order logic, validation, and CLI layers — plus structured logging and proper error handling throughout.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # package marker
│   ├── client.py            # Binance REST API wrapper (signing, requests, error handling)
│   ├── orders.py            # order placement logic + response formatting
│   ├── validators.py        # input validation (symbol, side, type, qty, price)
│   └── logging_config.py   # structured logging setup
├── cli.py                   # CLI entry point (argparse sub-commands)
├── logs/
│   └── trading_bot.log      # auto-created on first run
├── requirements.txt
├──.env                      # your API credentials
└── README.md
```

---

## Setup

1. Get API credentials from Binance Futures Testnet

Go to https://testnet.binancefuture.com
Log in with Google
On the dashboard, click "Generate Key"
Copy both the API Key and Secret Key — the secret is only shown once, so copy it immediately

2. Install dependencies

```bash
# Requires Python 3.8+
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Add your credentials to .env

BINANCE_TESTNET_API_KEY=your_api_key_here
BINANCE_TESTNET_API_SECRET=your_secret_key_here

---

## How to Run

Just run:
bashpython cli.py

---

You'll get an interactive prompt that walks you through everything:

Symbol (e.g. BTCUSDT): BTCUSDT

Side:
[1] BUY
[2] SELL
Enter choice (1/2): 1

Order Type:
[1] MARKET
[2] LIMIT
[3] STOP_MARKET (bonus)
Enter choice (1/2/3): 1

Quantity (e.g. 0.01): 0.01

---

You can also pass everything as flags if you prefer:
bash# MARKET order
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002

# LIMIT order

python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.002 --price 100000

# STOP_MARKET order (bonus 3rd order type)

python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.002 --stop-price 84000

---

## Sample Output

```
----------- Order Summary -----------
Symbol   : BTCUSDT
Side     : BUY
Type     : MARKET
Quantity : 0.01
-------------------------------------


====================================================
                  ORDER DETAILS
====================================================
Order ID        : 12554897899
Client Order ID : z4MKm2wmH49S45ixgEij7Z
Symbol          : BTCUSDT
Side            : BUY
Type            : MARKET
Status          : NEW
Quantity        : 0.010
Executed Qty    : 0.000
Average Price   : 0.00
Price           : 0.00
Stop Price      : 0.00
Time in Force   : GTC
Reduce Only     : False
Last Update     : 1772186909134
----------------------------------------------------

Order placed successfully ✔

```

---

## Logging

Logs are written to `logs/trading_bot.log` automatically (directory is created on first run).

Log format:

```
2025-02-27 09:12:01 | INFO     | trading_bot.client | Order placed successfully | orderId=4194437280 status=FILLED
```

## Requirements

- Python 3.8+
- `requests` >= 2.31.0
- A Binance Futures Testnet account with API credentials
