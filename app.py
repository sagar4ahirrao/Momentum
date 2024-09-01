import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Helper functions
def fetch_data(ticker, start_date, end_date):
    try:
        data = yf.download(ticker + ".NS", start=start_date, end=end_date)
        data = data[['Close']]
        return data
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame(columns=['Close'])

def calc_return(price, length):
    return price.pct_change(periods=length).shift(-length)

def calc_stddev(price, length):
    log_return = np.log(price / price.shift(1))
    stddev = log_return.rolling(window=length).std() * np.sqrt(252)
    return stddev

# Streamlit UI
st.title("Normalized Momentum Score Calculator")

# Dropdown list of Indian stock tickers
tickers = [
    'HUDCO', 'COCHINSHIP', 'ARE&M', 'EXIDEIND', 'CROMPTON', 'NATIONALUM', 'APARINDS', 'CDSL', 
    'GLENMARK', 'TITAGARH', 'MCX', 'NCC', 'HINDCOPPER', 'KARURVYSYA', 'NBCC', 'NAM-INDIA', 
    '360ONE', 'IEX', 'CENTURYTEX', 'MOTILALOFS', 'JWL', 'CASTROLIND', 'AEGISLOG', 'FINCABLES', 
    'EIHOTEL', 'GESHIP', 'CYIENT', 'BEML', 'IRCON', 'NATCOPHARM', 'SOBHA', 'REDINGTON', 'FINPIPE', 
    'BSOFT', 'SONATSOFTW', 'HSCL', 'HFCL', 'ENGINERSIN', 'MANAPPURAM', 'MGL', 'ACE', 'HBLPOWER', 
    'INTELLECT', 'GPIL', 'GRSE', 'GODFRYPHLP', 'IIFL', 'OLECTRA', 'PRAJIND', 'ZENSARTECH', 
    'TRITURBINE', 'NH', 'CHENNPETRO', 'CHAMBLFERT', 'NLCINDIA', 'KSB', 'INDIAMART', 'TANLA', 
    'GPPL', 'ELECON', 'AMBER', 'CANFINHOME', 'IOB', 'CIEINDIA', 'USHAMART', 'RITES', 'PNCINFRA', 
    'WELCORP', 'JYOTHYLAB', 'FSL', 'GNFC', 'CREDITACC', 'JINDALSAW', 'GSFC', 'TRIVENI', 'BLS', 
    'ASTRAZEN', 'FINEORG', 'PNBHOUSING', 'METROPOLIS', 'SAREGAMA', 'JBMA', 'ERIS', 'JKPAPER', 
    'PCBL', 'JKLAKSHMI', 'CGCL', 'MASTEK', 'GMDCLTD', 'GRAPHITE', 'CAPLIPOINT', 'QUESS', 
    'WELSPUNLIV', 'BIRLACORPN', 'AVANTIFEED', 'BALAMINES', 'RHIM', 'VIPIND', 'SUNTECK', 'GAEL'
]

ticker = st.selectbox("Select Stock Ticker", tickers)
start_date = st.date_input("Start Date", pd.to_datetime("2022-01-01"))
end_date = st.date_input("End Date", pd.to_datetime("today"))

length15d = st.slider("15-Day Period", min_value=1, max_value=50, value=15)
length1m = st.slider("1-Month Period", min_value=1, max_value=50, value=21)  # Approx. 21 trading days
lookback = st.slider("Lookback Period", min_value=1, max_value=500, value=252)

# Fetch data
data = fetch_data(ticker, start_date, end_date)
if data.empty:
    st.stop()

# Calculate Momentum Ratios
price = data['Close']
price = price.reindex(pd.date_range(start=start_date, end=end_date, freq='B')).ffill()

stddev = calc_stddev(price, length1m)  # Using length1m for stddev calculation
momentum_ratio_1m = calc_return(price, length1m) / stddev
momentum_ratio_15d = calc_return(price, length15d) / stddev

# Calculate Z-Scores
mean_mr1m = momentum_ratio_1m.rolling(window=lookback).mean()
std_mr1m = momentum_ratio_1m.rolling(window=lookback).std()
mean_mr15d = momentum_ratio_15d.rolling(window=lookback).mean()
std_mr15d = momentum_ratio_15d.rolling(window=lookback).std()

z_score_1m = (momentum_ratio_1m - mean_mr1m) / std_mr1m
z_score_15d = (momentum_ratio_15d - mean_mr15d) / std_mr15d

# Calculate Weighted Average Z Score
weighted_z_score = 0.5 * z_score_1m + 0.5 * z_score_15d

# Ensure lengths match by dropping NaN values
weighted_z_score = weighted_z_score.dropna()

# Calculate Normalized Momentum Score
normalized_momentum_score = np.where(weighted_z_score >= 0, 
                                      1 + weighted_z_score, 
                                      1 / (1 - weighted_z_score))

# Ensure the DataFrame has matching lengths
score_df = pd.DataFrame({
    'Date': weighted_z_score.index,
    'Normalized Momentum Score': normalized_momentum_score
})

# Display the results in a table
st.subheader(f"Normalized Momentum Score for {ticker}")
st.dataframe(score_df.set_index('Date'))
