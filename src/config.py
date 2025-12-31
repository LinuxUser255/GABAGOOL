#!/usr/bin/env python3

import os
from dotenv import load_dotenv


def load_config():
    load_dotenv()  # Load from .env file
    return {
        'prediction_market': os.getenv('MARKET', 'kalshi'),  # or 'polymarket'
        'api_key': os.getenv('API_KEY'),
        'api_secret': os.getenv('API_SECRET'),
        'dip_threshold': float(os.getenv('DIP_THRESHOLD', 0.05)),  # 5% dip to buy
        'target_avg_cost': float(os.getenv('TARGET_AVG_COST', 0.99)),  # Under $1 lock
        'pair': os.getenv('PAIR', 'BTC/USD'),  # Target pair
        'interval': os.getenv('INTERVAL', '15m')  # 15-minute outcomes
    }
