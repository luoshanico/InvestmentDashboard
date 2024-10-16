import yfinance as yf
import db_helpers as db

def get_pricing_data(ticker, asset_id):
    pricing_data = yf.download(ticker, period="5y", interval="1d")
    if pricing_data.size > 0:
        pricing_data = pricing_data.reset_index()
        pricing_data = pricing_data[['Date','Close']]
        pricing_data['Asset_ID'] = asset_id
        pricing_data = pricing_data[['Asset_ID','Date','Close']]
        pricing_data['Date'] = pricing_data['Date'].dt.strftime('%Y-%m-%d')
        pricing_data.rename(columns={'Close':'Price'})
        pricing_data_tuples = tuple(pricing_data.itertuples(index=False, name=None))
        return pricing_data_tuples
    else:
        return 0

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


