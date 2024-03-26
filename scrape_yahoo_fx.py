import pandas as pd
import aiohttp
import asyncio
import argparse
from typing import Literal
from datetime import datetime
from dateutil.parser import parse


def _build_yahoo_fx_url(base, target):
    return f"https://query1.finance.yahoo.com/v7/finance/download/{base}{target}%3DX"


async def get_yahoo_fx_rate_async(
    session: aiohttp.ClientSession,
    base: str,
    target: str,
    from_date: datetime,
    to_date: datetime,
    interval: Literal["1d", "1wk", "1mo"] = "1d",
    frequency: Literal["1d", "1wk", "1mo"] = "1d",
):
    url = _build_yahoo_fx_url(base, target)
    headers = {"User-Agent": "Mozilla/5.0"}
    params = {
        "period1": int(from_date.timestamp()),
        "period2": int(to_date.timestamp()),
        "interval": interval,
        "filter": "history",
        "frequency": frequency,
        "includeAdjustedClose": "true",
    }
    async with session.get(url, headers=headers, params=params) as response:
        response.raise_for_status()
        content = await response.content.read()
        content = content.decode()
        rows = content.split("\n")
        headers = rows[0].split(",")
        data = [row.split(",") for row in rows[1:]]
        df = pd.DataFrame(data, columns=headers)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date")
        df = df.apply(pd.to_numeric, errors="coerce")
        return df


async def fetch_all_async(
    currencies: list[str],
    from_date: datetime,
    to_date: datetime,
    interval: Literal["1d", "1wk", "1mo"] = "1d",
    frequency: Literal["1d", "1wk", "1mo"] = "1d",
):
    pairs_to_fetch = []
    for i, base in enumerate(currencies):
        for target in currencies[i + 1 :]:
            pairs_to_fetch.append((base, target))

    fx_rates = {}
    async with aiohttp.ClientSession() as session:
        tasks = []
        for base, target in pairs_to_fetch:
            tasks.append(get_yahoo_fx_rate_async(session, base, target, from_date, to_date, interval, frequency))
        results = await asyncio.gather(*tasks)
        for (base, target), df in zip(pairs_to_fetch, results):
            fx_rates[f"{base} {target}"] = df  # normal rate
            fx_rates[f"{target} {base}"] = 1 / df  # reverse rate
            fx_rates[f"{base} {base}"] = df**0  # identity rate

    fx_rates[currencies[-1] + " " + currencies[-1]] = fx_rates[currencies[0] + " " + currencies[0]] # add the last identity rate - a little hacky
    return fx_rates

def fetch_all(
    currencies: list[str],
    from_date: datetime,
    to_date: datetime,
    interval: Literal["1d", "1wk", "1mo"] = "1d",
    frequency: Literal["1d", "1wk", "1mo"] = "1d",
):
    fx_rates = asyncio.run(fetch_all_async(currencies, from_date, to_date, interval, frequency))
    return fx_rates


def get_closing_fx_rates(
        currencies: list[str],
        from_date: datetime,
        to_date: datetime,
        interval: Literal["1d", "1wk", "1mo"] = "1d",
        frequency: Literal["1d", "1wk", "1mo"] = "1d",
):
    fx_rates = fetch_all(currencies, from_date, to_date, interval, frequency)
    _closing_rates = {k: v["Close"] for k, v in fx_rates.items()}
    closing_rates = pd.DataFrame(_closing_rates)
    return closing_rates


def get_opening_fx_rates(
    currencies: list[str],
    from_date: datetime,
    to_date: datetime,
    interval: Literal["1d", "1wk", "1mo"] = "1d",
    frequency: Literal["1d", "1wk", "1mo"] = "1d",
):
    fx_rates = fetch_all(currencies, from_date, to_date, interval, frequency)
    _opening_rates = {k: v["Open"] for k, v in fx_rates.items()}
    opening_rates = pd.DataFrame(_opening_rates)
    return opening_rates


def get_high_fx_rates(
    currencies: list[str],  
    from_date: datetime,
    to_date: datetime,
    interval: Literal["1d", "1wk", "1mo"] = "1d",
    frequency: Literal["1d", "1wk", "1mo"] = "1d",
):
    fx_rates = fetch_all(currencies, from_date, to_date, interval, frequency)
    _high_rates = {k: v["High"] for k, v in fx_rates.items()}
    high_rates = pd.DataFrame(_high_rates)
    return high_rates


def get_low_fx_rates(
    currencies: list[str],
    from_date: datetime,
    to_date: datetime,
    interval: Literal["1d", "1wk", "1mo"] = "1d",
    frequency: Literal["1d", "1wk", "1mo"] = "1d",
):
    fx_rates = fetch_all(currencies, from_date, to_date, interval, frequency)
    _low_rates = {k: v["Low"] for k, v in fx_rates.items()}
    low_rates = pd.DataFrame(_low_rates)
    return low_rates


def scrape_yahoo_fx(
        fx_type: Literal["closing", "opening", "high", "low"],
        currencies: list[str],
        from_date: datetime,
        to_date: datetime = None,
        interval: Literal["1d", "1wk", "1mo"] = "1d",
        frequency: Literal["1d", "1wk", "1mo"] = "1d",
) -> pd.DataFrame:
    """
    Scrape foreign exchange (FX) data from Yahoo Finance.

    Args:
        fx_type (str): The type of FX data to scrape. This can be 'closing', 'opening', 'high', or 'low'.
        currencies (list): The currencies to scrape data for. This should be a list of currency codes.
        from_date (datetime): The start date for the data to scrape.
        to_date (datetime, optional): The end date for the data to scrape. If not provided, the current date will be used.
        interval (str, optional): The interval for fetching data, e.g. '1d', '1wk', '1mo'. If not provided, '1d' will be used.
        frequency (str, optional): The frequency for fetching data, e.g. '1d', '1wk', '1mo'. If not provided, '1d' will be used.

    Returns:
        pandas.DataFrame: A DataFrame containing the scraped FX data.
    """
    if to_date is None:
        to_date = datetime.now()
    if fx_type.lower() == "closing":
        df = get_closing_fx_rates(currencies, from_date, to_date, interval, frequency)
    elif fx_type.lower() == "opening":
        df = get_opening_fx_rates(currencies, from_date, to_date, interval, frequency)
    elif fx_type.lower() == "high":
        df = get_high_fx_rates(currencies, from_date, to_date, interval, frequency)
    elif fx_type.lower() == "low":
        df = get_low_fx_rates(currencies, from_date, to_date, interval, frequency)
    else:
        raise ValueError("Invalid FX rate type. Choose from closing, opening, high, low")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Yahoo Finance for FX rates")
    parser.add_argument("--fx_type", type=str, help="Type of FX rate to fetch", required=True)
    parser.add_argument("--from", type=str, help="Start date for fetching", required=True)
    parser.add_argument("--to", type=str, help="End date for fetching", required=False, default=None)
    parser.add_argument("--interval", type=str, help="Interval for fetching, e.g. 1d, 1wk, 1mo", default="1d")
    parser.add_argument("--frequency", type=str, help="Frequency for fetching, e.g. 1d, 1wk, 1mo", default="1d")
    parser.add_argument("--o", type=str, help="Output file for CSV, if None, displays in console", required=False, default=None)
    parser.add_argument("--currencies", nargs="+", help="List of currencies to fetch", required=True)
    args = parser.parse_args()
    fx_type = args.fx_type
    output = args.o
    currencies = args.currencies
    from_date = parse(getattr(args, "from"))
    to_date = None if args.to is None else parse(args.to)
    interval = args.interval
    frequency = args.frequency

    if len(currencies) < 2:
        raise ValueError("Please provide at least two currencies to fetch")
    if fx_type.lower() not in ["closing", "opening", "high", "low"]:
        raise ValueError("Invalid FX rate type. Choose from closing, opening, high, low")
    currencies = [currency.upper() for currency in currencies]
    if any([len(currency) != 3 for currency in currencies]):
        raise ValueError("Currency codes must be 3 characters long")
    
    df = scrape_yahoo_fx(fx_type, currencies, from_date, to_date, interval, frequency)
    if output:
        df.to_csv(output)
    else:
        # print to console nicely
        print(df.to_markdown())

