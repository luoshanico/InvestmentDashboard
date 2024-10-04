import yfinance as yf

def get_pricing_data(ticker):
    stock_data = yf.download(ticker, period="5y", interval="1d")
    stock_data_index_reset = stock_data.reset_index()
    pricing_data = stock_data_index_reset[['Date','Close']]
    pricing_data['Asset'] = ticker
    pricing_data = pricing_data[['Asset','Date','Close']]
    pricing_data['Date'] = pricing_data['Date'].dt.strftime('%Y-%m-%d')
    pricing_data.rename(columns={'Close':'Price'})
    pricing_data_tuples = tuple(pricing_data.itertuples(index=False, name=None))
    return pricing_data_tuples








