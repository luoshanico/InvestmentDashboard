import yfinance as yf
import pandas as pd

def get_pricing_data(ticker, asset_id):
    pricing_data = yf.download(ticker, period="5y", interval="1d")
    pricing_data = pricing_data.reset_index()
    pricing_data = pricing_data[['Date','Close']]
    pricing_data['Asset_ID'] = asset_id
    pricing_data = pricing_data[['Asset_ID','Date','Close']]
    pricing_data['Date'] = pricing_data['Date'].dt.strftime('%Y-%m-%d')
    pricing_data.rename(columns={'Close':'Price'}, inplace=True)
    return pricing_data


def get_fx_data(ticker, currency):
    fx_data = yf.download(ticker, period="5y", interval="1d")
    fx_data = fx_data.reset_index()
    fx_data = fx_data[['Date','Close']]
    fx_data['Currency'] = currency
    fx_data = fx_data[['Date','Currency','Close']]
    fx_data['Date'] = fx_data['Date'].dt.strftime('%Y-%m-%d')
    fx_data.rename(columns={'Close':'Rate'}, inplace=True)
    return fx_data

    

def convert_prices_to_gbp(prices, fx_rates):
     # Join dataframes on date
    prices_gbp = pd.merge(prices, fx_rates, on='Date', how='left')
    
    # Calculate GBP price
    prices_gbp['Price (GBP)'] = prices_gbp['Price'] / prices_gbp['Rate']
    
    # Drop columns and rename
    prices_gbp = prices_gbp[['Asset_ID','Date','Price (GBP)']]
    prices_gbp = prices_gbp.rename(columns={'Price (GBP)': 'Price'})
    
    return prices_gbp


def get_stock_info(ticker):
    stock_info = yf.Ticker(ticker)
    
    if len(stock_info.info) == 1:
        stock_name = ''
        stock_cat = ''
        stock_currency = ''
    else:
        stock_name = stock_info.info['longName']
        stock_cat = stock_info.info['quoteType']
        stock_currency = stock_info.info['currency']
        
    stock_info_dict = {
        'stock_name':stock_name,
        'stock_cat':stock_cat,
        'stock_currency':stock_currency
        }
    
    return stock_info_dict


