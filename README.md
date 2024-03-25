# Yahoo-FX-Scraper
This is a simple script that will scrape recent daily FX data from Yahoo Finance.

## Usage
The script can be run from the command line like so:

`python scrape_yahoo_fx.py --fx_type=closing --o=rates.csv --currencies USD GBP AUD`

You can also import and use the function `scrape_yahoo_fx` to pull the data as a pandas DataFrame for use within your code.
``` python
from scrape_yahoo_fx import scrape_yahoo_fx

currencies = [
    "USD",
    "GBP",
    "AUD"
]
df = scrape_yahoo_fx(fx_type = "closing", currencies=currencies)

...
```

The scraper will produce an output CSV/DataFrame with the following format, where each column is in the format "BASE TARGET".

| Date       | USD GBP | GBP USD | USD USD | USD AUD | AUD USD | GBP AUD | AUD GBP | GBP GBP | AUD AUD |
|------------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
| 2024-03-25 | 0.79    | 1.26    | 1.00    | 1.53    | 0.65    | 1.93    | 0.52    | 1.00    | 1.00    |
| 2024-03-22 | 0.79    | 1.27    | 1.00    | 1.52    | 0.66    | 1.93    | 0.52    | 1.00    | 1.00    |
| 2024-03-21 | 0.78    | 1.28    | 1.00    | 1.52    | 0.66    | 1.94    | 0.52    | 1.00    | 1.00    |
| 2024-03-20 | 0.79    | 1.27    | 1.00    | 1.53    | 0.65    | 1.95    | 0.51    | 1.00    | 1.00    |
| ...        | ...     | ...     | ...     | ...     | ...     | ...     | ...     | ...     | ...     |

This will only scrape recent daily data. If people ask for it, I will spin something up that can pull historical data from different periods and at different frequencies. 

