# Yahoo-FX-Scraper
This is a simple script that will scrape recent daily FX data from Yahoo Finance.

## Usage

## Command Line Execution

You can run the `scrape_yahoo_fx.py` script directly from the command line. Here's how to do it:

```bash
python scrape_yahoo_fx.py --fx_type=closing --from=2024-1-1 --to=2024-3-1 --interval=1d --frequency=1d --currencies USD GBP AUD --o=example_rates.csv
```

- `--fx_type`: The type of FX data to scrape. This can be `closing`, `opening`, `high`, or `low`.
- `--from`: The start date for the data to scrape. Suggest the format `YYYY-MM-DD`, others will work.
- `--to`: The end date for the data to scrape. If not provided, the current date will be used.
- `--interval`: The interval for fetching data, e.g. `1d`, `1wk`, `1mo`. If not provided, `1d` will be used.
- `--frequency`: The frequency for fetching data, e.g. `1d`, `1wk`, `1mo`. If not provided, `1d` will be used.
- `--currencies`: The currencies to scrape data for. This should be a space-separated list of currency codes.
- `--o`: The name of the output file where the scraped data will be saved. This should be a `.csv` file. If not provided, the data will be printed to the console.

## Using the `scrape_yahoo_fx` Function

The `scrape_yahoo_fx` function allows you to scrape foreign exchange (FX) data from Yahoo Finance directly within your Python code. Here's an example of how to use it:

```python
from scrape_yahoo_fx import scrape_yahoo_fx
from datetime import datetime

# Define the currencies to scrape data for
currencies = ["USD", "GBP", "AUD"]

# Call the function
df = scrape_yahoo_fx(
    fx_type="closing", 
    currencies=currencies,
    from_date=datetime(2024,1,1),
    to_date=datetime(2024,3,1),
    interval='1d',
    frequency='1d'
)

# The function returns a pandas DataFrame
print(df.head())
```
The scraper will produce an output CSV/DataFrame with the following format, where each column is in the format "BASE TARGET".

| Date       | USD GBP | GBP USD | USD USD | USD AUD | AUD USD | GBP AUD | AUD GBP | GBP GBP | AUD AUD |
|------------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
| 2024-01-01 | 0.79    | 1.27    | 1.00    | 1.47    | 0.68    | 1.87    | 0.54    | 1.00    | 1.00    |
| 2024-01-02 | 0.79    | 1.27    | 1.00    | 1.47    | 0.68    | 1.87    | 0.54    | 1.00    | 1.00    |
| 2024-01-03 | 0.79    | 1.26    | 1.00    | 1.48    | 0.68    | 1.87    | 0.54    | 1.00    | 1.00    |
| 2024-01-04 | 0.79    | 1.27    | 1.00    | 1.48    | 0.67    | 1.88    | 0.53    | 1.00    | 1.00    |
| 2024-01-05 | 0.79    | 1.27    | 1.00    | 1.49    | 0.67    | 1.89    | 0.53    | 1.00    | 1.00    |
| ...        | ...     | ...     | ...     | ...     | ...     | ...     | ...     | ...     | ...     |


Hopefully someone finds this little script useful, enjoy!