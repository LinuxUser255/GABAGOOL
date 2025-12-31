#!/usr/bin/env python3
import time
import logging


class GabagoolStrategy:
    def __init__(self, api, config):
        self.api = api
        self.config = config
        self.positions = {'YES': {'cost': 0, 'units': 0}, 'NO': {'cost': 0, 'units': 0}}  # Track YES/NO

# start bot: begin main trading loop
    def run(self):
        while True:
            self.monitor_and_scalp() # called here, the method is below
            time.sleep(60)  # Check every minute

    def monitor_and_scalp(self): # fetch current prices and check for dips
        yes_price = self.api.get_price(self.config['pair'], 'YES')
        no_price = self.api.get_price(self.config['pair'], 'NO')

        # Detect asymmetric dip
        if yes_price < (1 - self.config['dip_threshold']):
            self.buy_dip('YES', amount=100, price=yes_price)  # Example amount
        elif no_price < (1 - self.config['dip_threshold']):
            self.buy_dip('NO', amount=100, price=no_price)

        # Check lock profit
        has_yes_position = self.positions['YES']['units'] > 0
        has_no_position = self.positions['NO']['units'] > 0
        
        if has_yes_position and has_no_position:
            avg_yes_no = (self.positions['YES']['cost'] + self.positions['NO']['cost']) / 2
        else:
            avg_yes_no = float('inf')
        
        if avg_yes_no < self.config['target_avg_cost']:
            logging.info(f"Profit locked! Avg cost: {avg_yes_no}")

# Execute the dip buy order 
    def buy_dip(self, side, amount, price):
        order = self.api.place_order(self.config['pair'] + side, 'buy', amount, price)
        cost = amount * price
        self.positions[side]['units'] += amount
        # Update average cost using weighted average
        old_total_cost = self.positions[side]['cost'] * (self.positions[side]['units'] - amount)
        new_total_cost = old_total_cost + cost
        self.positions[side]['cost'] = new_total_cost / self.positions[side]['units']
        
        logging.info(f"Bought {side} dip: {amount} at {price}")
