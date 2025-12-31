
# GABAGOOL Bot Execution Flow

## Entry Point: `main.py`

### 1. Script Initialization

```python
if __name__ == "__main__":
    main()
```

- Python checks if the script is being run directly (not imported)
- If true, calls the `main()` function

---

### 2. Main Function Execution
```python
def main():
    config = load_config()
    api = PredictionMarketAPI(config)
    strategy = GabagoolStrategy(api, config)
    logging.info("GABAGOOL bot starting...")
    strategy.run()
```

#### Step 2.1: Load Configuration
- **Function**: `load_config()` from `src/config.py`
- **Purpose**: Loads bot configuration including:
  - API credentials (`api_key`, `api_secret`)
  - Trading pair (e.g., `'BTC/USD'`)
  - Prediction market platform (`'kalshi'` or `'polymarket'`)
  - Strategy parameters:
    - `dip_threshold`: Minimum price drop to trigger buy
    - `target_avg_cost`: Target average cost for profit lock
- **Returns**: Dictionary containing all configuration values

#### Step 2.2: Initialize Market API
- **Class**: `PredictionMarketAPI(config)` from `src/market_api.py`
- **Constructor Flow**:
  ```python
  def __init__(self, config):
      self.config = config
      self.exchange = self._init_exchange()
  ```
  - Stores configuration
  - Calls `_init_exchange()` to set up exchange connection
  - **Exchange Initialization**:
    - Checks `config['prediction_market']`
    - Currently uses placeholder (ccxt.binance) for both Kalshi and Polymarket
    - Logs warning about simulation mode
- **Purpose**: Provides interface for market data and order execution

#### Step 2.3: Initialize Trading Strategy
- **Class**: `GabagoolStrategy(api, config)` from `src/strategy.py`
- **Constructor Flow**:
  ```python
  def __init__(self, api, config):
      self.api = api
      self.config = config
      self.positions = {'YES': {'cost': 0, 'units': 0}, 'NO': {'cost': 0, 'units': 0}}
  ```
  - Stores API and config references
  - Initializes position tracking for YES/NO contracts
  - Each position tracks:
    - `cost`: Average cost per unit
    - `units`: Total units held

#### Step 2.4: Start Bot
- Logs startup message
- Calls `strategy.run()` to begin main trading loop

---

### 3. Main Trading Loop: `strategy.run()`
```python
def run(self):
    while True:
        self.monitor_and_scalp()
        time.sleep(60)  # Check every minute
```
- **Infinite loop** that runs continuously
- Each iteration:
  1. Calls `monitor_and_scalp()` to check market and execute trades
  2. Sleeps for 60 seconds before next check

---

### 4. Market Monitoring: `strategy.monitor_and_scalp()`

#### Step 4.1: Fetch Current Prices
```python
yes_price = self.api.get_price(self.config['pair'], 'YES')
no_price = self.api.get_price(self.config['pair'], 'NO')
```
- **API Call**: `get_price(pair, side)` from `PredictionMarketAPI`
- **Flow**:
  ```python
  def get_price(self, pair, side):
      ticker = self.exchange.fetch_ticker(pair)
      return ticker['last']
  ```
  - Fetches ticker data from exchange
  - Returns last traded price
  - **Note**: Currently doesn't differentiate between YES/NO (placeholder logic)

#### Step 4.2: Detect Asymmetric Dips
```python
if yes_price < (1 - self.config['dip_threshold']):
    self.buy_dip('YES', amount=100, price=yes_price)
elif no_price < (1 - self.config['dip_threshold']):
    self.buy_dip('NO', amount=100, price=no_price)
```
- **Logic**: If price drops below `(1 - dip_threshold)`, trigger buy
- **Example**: If `dip_threshold = 0.1`, buy when price < 0.9
- Checks YES first, then NO (asymmetric detection)
- Hardcoded amount of 100 units

#### Step 4.3: Execute Dip Buy
```python
def buy_dip(self, side, amount, price):
    order = self.api.place_order(self.config['pair'] + side, 'buy', amount, price)
    cost = amount * price
    self.positions[side]['units'] += amount
    self.positions[side]['cost'] = ((self.positions[side]['cost'] * self.positions[side]['units'] - cost) + cost) / self.positions[side]['units']
    logging.info(f"Bought {side} dip: {amount} at {price}")
```
- **Order Placement**:
  ```python
  def place_order(self, pair, side, amount, price, paper=True):
      if paper:
          logging.info(f"[PAPER] Placed {side} order for {amount} {pair} at {price}")
          return {'id': 'simulated'}
      # Real order logic (not executed in paper mode)
  ```
  - Default is **paper trading** (simulation)
  - Logs order without executing on exchange
  - Returns simulated order ID

- **Position Update**:
  - Adds units to position
  - Recalculates average cost using weighted average formula
  - Logs the purchase

#### Step 4.4: Check Profit Lock Condition
```python
has_yes_position = self.positions['YES']['units'] > 0
has_no_position = self.positions['NO']['units'] > 0

if has_yes_position and has_no_position:
    avg_yes_no = (self.positions['YES']['cost'] + self.positions['NO']['cost']) / 2
else:
    avg_yes_no = float('inf')

if avg_yes_no < self.config['target_avg_cost']:
    logging.info(f"Profit locked! Avg cost: {avg_yes_no}")
```
- **Profit Lock Logic**:
  - Only possible when holding BOTH YES and NO positions
  - Calculates average cost across both positions
  - If average < target (e.g., < $1.00), profit is guaranteed regardless of outcome
  - **Example**: 
    - YES cost: $0.40, NO cost: $0.50
    - Average: $0.45
    - If target is $1.00, profit is locked ($0.55 per contract)

---

## Execution Flow Summary

```
main.py
  └─> main()
       ├─> load_config() → Returns config dict
       ├─> PredictionMarketAPI(config)
       │    └─> _init_exchange() → Sets up exchange connection
       ├─> GabagoolStrategy(api, config)
       │    └─> Initializes positions tracking
       └─> strategy.run()
            └─> Infinite loop (every 60 seconds):
                 └─> monitor_and_scalp()
                      ├─> get_price('YES') → Fetch YES price
                      ├─> get_price('NO') → Fetch NO price
                      ├─> Check for dips:
                      │    └─> If dip detected → buy_dip()
                      │         ├─> place_order() → Execute trade (paper mode)
                      │         └─> Update positions & avg cost
                      └─> Check profit lock:
                           └─> If avg cost < target → Log profit locked
```

---

## Key States & Data Flow

### Configuration State
- Loaded once at startup
- Immutable during execution
- Contains all strategy parameters

### Position State
- Mutable, updated on each trade
- Tracks YES and NO positions separately
- Persists across loop iterations

### Market Data Flow
1. Exchange → `fetch_ticker()` → Raw ticker data
2. `get_price()` → Extracts last price
3. `monitor_and_scalp()` → Evaluates prices
4. Decision: Buy or wait
5. If buy → Update positions → Log

### Order Flow (Paper Mode)
1. `buy_dip()` called with side, amount, price
2. `place_order()` logs simulated order
3. Position tracking updated locally
4. No actual exchange interaction

---

## Notes

- **Current State**: Paper trading mode (simulation only)
- **Loop Frequency**: 60-second intervals
- **Hardcoded Values**: 
  - Trade amount: 100 units
  - Sleep interval: 60 seconds
- **Placeholders**:
  - Exchange API (using Binance as placeholder)
  - YES/NO price differentiation not implemented
  - Real order execution disabled
```