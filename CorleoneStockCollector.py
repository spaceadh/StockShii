# stock_analyzer.py

import os
import re
import sys
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Define the cache directory
CACHE_DIR = 'cache'

# Updated MARKETS dictionary
MARKETS = {
    "NYSE": [
        "IBM", "GE", "T", "VZ",
        "JNJ", "JPM", "BAC", "WMT",
        "DIS", "KO", "MCD", "PFE",
        "CAT", "BA", "MMM", "XOM",
        "CVX", "GS", "MS", "INTC"
    ],
    "NASDAQ": [
        "AAPL", "MSFT", "GOOGL", "AMZN",
        "FB", "NFLX", "NVDA", "TSLA",
        "ADBE", "PYPL", "CMCSA", "INTC",
        "CSCO", "PEP", "QCOM", "AVGO",
        "TXN", "AMD", "GILD", "AMGN"
    ],
    "London Stock Exchange": [
        "HSBA", "BP", "VOD", "GSK",
        "BARC", "AZN", "RIO", "ULVR",
        "DGE", "BT.A", "ITRK", "RBS",
        "BATS", "GLEN", "IMB", "LLOY",
        "SBRY", "TSCO", "VED", "WPP"
    ],
    "Toronto Stock Exchange": [
        "RY", "TD", "BNS", "ENB",
        "BMO", "CM", "TRP", "SU",
        "SHOP", "MFC", "CNQ", "BCE",
        "TD", "CNR", "FTS", "ABX",
        "CVE", "SU", "IMO", "TEL"
    ],
    "Australian Securities Exchange": [
        "CBA", "BHP", "ANZ", "WBC",
        "NAB", "CSL", "WES", "MQG",
        "WOR", "TLS", "WOW", "RIO",
        "FMG", "SCG", "GMG", "SUN",
        "TLS", "AMP", "COL", "SGP"
    ],
    "Deutsche Börse Xetra": [
        "BMW", "SAP", "DTE", "BAS",
        "ALV", "VOW3", "SIE", "LIN",
        "BAYN", "DBK", "RWE", "BEI",
        "ADS", "FME", "CON", "HEI",
        "MRK", "EOAN", "MTX", "TKA"
    ],
    "Tokyo Stock Exchange": [
        "7203", "6758", "9432", "9984",
        "8306", "6954", "8308", "8035",
        "8031", "6752", "9433", "6367",
        "6971", "4502", "7201", "6861",
        "7751", "8038", "8591", "8304"
    ],
    "Hong Kong Stock Exchange": [
        "0700", "0941", "3690", "2388",
        "HKD1", "2318", "2382", "883",
        "388", "3694", "1928", "2628",
        "0005", "2319", "8163", "2313",
        "1810", "2383", "366", "3691"
    ],
    "Euronext Paris": [
        "AIR", "BNP", "ENGI", "OR",
        "GLE", "MC", "SAN", "VIE",
        "DSY", "AI", "ATO", "EL",
        "FTI", "RNO", "UG", "ACA",
        "ACA", "DG", "KER", "MLE"
    ],
    "Swiss Exchange": [
        "NESN", "NOVN", "ROG", "UBSG",
        "CSGN", "ZURN", "SREN", "ABB",
        "GLEN", "SCMN", "LONN", "ADEN",
        "SLHN", "SPSN", "SQN", "BAER",
        "UHR", "SIKA", "TEMN", "LOGN"
    ]
}

def list_markets():
    print("\nAvailable Markets:")
    for idx, market in enumerate(MARKETS.keys(), start=1):
        print(f"{idx}. {market}")

def get_market_choice():
    while True:
        try:
            choice = int(input("\nSelect a market by entering the corresponding number: "))
            if 1 <= choice <= len(MARKETS):
                market = list(MARKETS.keys())[choice - 1]
                print(f"\nYou selected: {market}")
                return market
            else:
                print(f"Please enter a number between 1 and {len(MARKETS)}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def list_tickers(market):
    print(f"\nAvailable Tickers in {market}:")
    tickers = MARKETS[market]
    for idx, ticker in enumerate(tickers, start=1):
        print(f"{idx}. {ticker}")

def get_ticker_choices(market):
    tickers = MARKETS[market]
    while True:
        choices = input("\nEnter the numbers of the tickers you want to select (comma-separated for multiple, e.g., 1,3,4): ")
        # Validate input pattern: numbers separated by commas
        if re.fullmatch(r'(\d+,?)*\d+', choices.strip()):
            indices = [int(num.strip()) for num in choices.split(",")]
            if all(1 <= idx <= len(tickers) for idx in indices):
                selected_tickers = [tickers[idx - 1] for idx in indices]
                print(f"\nYou selected: {', '.join(selected_tickers)}")
                return selected_tickers
            else:
                print(f"Please enter numbers between 1 and {len(tickers)}.")
        else:
            print("Invalid format. Please enter numbers separated by commas (e.g., 1,3,4).")

def get_date(prompt):
    while True:
        date_str = input(f"{prompt} (YYYY-MM-DD): ").strip()
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}', date_str):
            return date_str
        else:
            print("Invalid date format. Please enter the date in YYYY-MM-DD format.")

def download_and_cache_data(tickers, start_date, end_date):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    
    data = {}
    for ticker in tickers:
        sanitized_ticker = ticker.replace(".", "_")  # Replace '.' with '_' for file naming
        file_name = f"{sanitized_ticker}_{start_date}_{end_date}.csv"
        file_path = os.path.join(CACHE_DIR, file_name)
        
        if os.path.exists(file_path):
            print(f"\nLoading cached data for {ticker} from {file_path}")
            stock_data = pd.read_csv(file_path, index_col='Date', parse_dates=True)
        else:
            print(f"\nDownloading data for {ticker}...")
            try:
                stock_data = yf.download(ticker, start=start_date, end=end_date)
                if stock_data.empty:
                    print(f"No data found for {ticker} in the specified date range.")
                    continue
                stock_data.to_csv(file_path)
                print(f"Data saved to {file_path}")
            except Exception as e:
                print(f"Error downloading data for {ticker}: {e}")
                continue
        data[ticker] = stock_data
    return data

def plot_data(data, tickers, start_date, end_date):
    plt.figure(figsize=(14, 8))
    
    for ticker in tickers:
        if ticker not in data:
            print(f"Skipping {ticker} as no data was downloaded.")
            continue
        stock_data = data[ticker]
        if stock_data.empty:
            print(f"No data to plot for {ticker}.")
            continue
        
        # Plot Opening Price
        plt.plot(stock_data.index, stock_data['Open'], label=f'{ticker} Open', linestyle='-', alpha=0.7)
        
        # Plot Closing Price
        plt.plot(stock_data.index, stock_data['Close'], label=f'{ticker} Close', linestyle='-', alpha=0.9)
        
        # Calculate Moving Averages
        stock_data['MA20'] = stock_data['Close'].rolling(window=20).mean()
        stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()
        
        # Plot Moving Averages
        plt.plot(stock_data.index, stock_data['MA20'], linestyle='--', label=f'{ticker} MA20')
        plt.plot(stock_data.index, stock_data['MA50'], linestyle=':', label=f'{ticker} MA50')
    
    plt.title('Stock Opening & Closing Prices with Moving Averages')
    plt.xlabel('Date')
    plt.ylabel('Price ($)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # Save the plot as an image
    # Create a safe filename by replacing special characters
    safe_tickers = "_".join(tickers).replace("/", "_")
    filename = f"stock_plot_{safe_tickers}_{start_date}_to_{end_date}.png"
    plt.savefig(filename)
    print(f"\nPlot saved as {filename}")
    
    # Display the plot
    plt.show()

def main():
    print("=== Stock Data Analyzer ===")
    
    # Step 1: List and select market
    list_markets()
    market = get_market_choice()
    
    # Step 2: List and select tickers
    list_tickers(market)
    selected_tickers = get_ticker_choices(market)
    
    # Step 3: Get date range
    print("\nEnter the date range for the stock data:")
    start_date = get_date("Start Date")
    end_date = get_date("End Date")
    
    # Validate date range
    if start_date > end_date:
        print("\nError: Start date cannot be after end date.")
        sys.exit(1)
    
    print("\n=== Selection Summary ===")
    print(f"Market: {market}")
    print(f"Tickers: {', '.join(selected_tickers)}")
    print(f"Date Range: {start_date} to {end_date}")
    
    # Step 4: Download and cache data
    data = download_and_cache_data(selected_tickers, start_date, end_date)
    
    if not data:
        print("\nNo data was downloaded. Exiting.")
        sys.exit(1)
    
    # Step 5: Filter data (drop rows with missing values)
    for ticker in selected_tickers:
        if ticker in data:
            original_length = len(data[ticker])
            data[ticker].dropna(inplace=True)
            filtered_length = len(data[ticker])
            print(f"\nFiltered data for {ticker}: {filtered_length} records remaining (dropped {original_length - filtered_length}).")
    
    # Step 6: Plot data
    plot_data(data, selected_tickers, start_date, end_date)

if __name__ == "__main__":
    main()
