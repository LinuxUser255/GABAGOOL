#!/usr/bin/env python3

import warnings

warnings.filterwarnings('ignore', category=UserWarning, module='pkg_resources')

import logging
from src.config import load_config
from src.market_api import PredictionMarketAPI
from src.strategy import GabagoolStrategy

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')


def main():
    config = load_config()
    api = PredictionMarketAPI(config)
    strategy = GabagoolStrategy(api, config)

    logging.info("GABAGOOL bot starting...")
    strategy.run()  # Loop for monitoring/dipping


if __name__ == "__main__":
    main()
