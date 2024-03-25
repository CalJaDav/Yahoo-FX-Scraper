import sys
import requests
import bs4 as soup
import pandas as pd
import aiohttp
import asyncio
import argparse


def _build_yahoo_fx_url(base, target):
    return f"https://finance.yahoo.com/quote/{base}{target}%3DX/history"

async def get_yahoo_fx_rate_async(session: aiohttp.ClientSession, base, target):
    url = _build_yahoo_fx_url(base, target)
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    async with session.get(url, headers=headers) as response:
        response.raise_for_status()
        html = soup.BeautifulSoup(await response.text(), 'html.parser')
        table = html.find('table')
        headers = [header.text for header in table.find_all('th')]
        body = table.findNext('tbody')
        rows = body.find_all('tr')
        data = []
        for row in rows:
            data.append([cell.text for cell in row.find_all('td')])

        df = pd.DataFrame(data, columns=headers)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        df = df.apply(pd.to_numeric, errors='coerce')

        return df
    
async def fetch_all(currencies):

    pairs_to_fetch = []
    for i, base in enumerate(currencies):
        for target in currencies[i+1:]:
            pairs_to_fetch.append((base, target))
    
    fx_rates = {}
    async with aiohttp.ClientSession() as session:
        tasks = []
        for base, target in pairs_to_fetch:
            tasks.append(get_yahoo_fx_rate_async(session, base, target))
        results = await asyncio.gather(*tasks)
        for (base, target), df in zip(pairs_to_fetch, results):
            fx_rates[f"{base} {target}"] = df # normal rate
            fx_rates[f"{target} {base}"] = 1/df # reverse rate
            fx_rates[f"{base} {base}"] = df**0 # identity rate
    fx_rates[currencies[-1]+" "+currencies[-1]] = fx_rates[currencies[0]+" "+currencies[0]] # add the last identity rate
    return fx_rates

def get_all_closing_fx_rates(currencies):
    fx_rates = asyncio.run(fetch_all(currencies))
    _closing_rates = {k: v['Close*'] for k, v in fx_rates.items()}
    closing_rates = pd.DataFrame(_closing_rates)
    return closing_rates

def get_all_opening_fx_rates(currencies):
    fx_rates = asyncio.run(fetch_all(currencies))
    _opening_rates = {k: v['Open'] for k, v in fx_rates.items()}
    opening_rates = pd.DataFrame(_opening_rates)
    return opening_rates

def get_all_high_fx_rates(currencies):
    fx_rates = asyncio.run(fetch_all(currencies))
    _high_rates = {k: v['High'] for k, v in fx_rates.items()}
    high_rates = pd.DataFrame(_high_rates)
    return high_rates

def get_all_low_fx_rates(currencies):
    fx_rates = asyncio.run(fetch_all(currencies))
    _low_rates = {k: v['Low'] for k, v in fx_rates.items()}
    low_rates = pd.DataFrame(_low_rates)
    return low_rates

def scrape_yahoo_fx(fx_type, currencies) -> pd.DataFrame:
    if fx_type.lower() == 'closing':
        df = get_all_closing_fx_rates(currencies)
    elif fx_type.lower() == 'opening':
        df = get_all_opening_fx_rates(currencies)
    elif fx_type.lower() == 'high':
        df = get_all_high_fx_rates(currencies)
    elif fx_type.lower() == 'low':
        df = get_all_low_fx_rates(currencies)
    else:
        raise ValueError("Invalid FX rate type. Choose from closing, opening, high, low")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape Yahoo Finance for FX rates')
    parser.add_argument('--fx_type', type=str, help='Type of FX rate to fetch', required=True)
    parser.add_argument('--o', type=str, help='Output file', required=True)
    parser.add_argument('--currencies', nargs='+', help='List of currencies to fetch', required=True)
    args = parser.parse_args()
    fx_type = args.fx_type
    output = args.o
    currencies = args.currencies
    
    if len(currencies) < 2:
        raise ValueError("Please provide at least two currencies to fetch")
    if output is None or output == '':
        raise ValueError("Please provide an output file")
    
    df = scrape_yahoo_fx(fx_type, currencies)
    df.to_csv(output)
  