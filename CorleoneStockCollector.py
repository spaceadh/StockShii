# stock_analyzer.py

import os
import re
import sys
import subprocess
import pkg_resources
import json 

# List of required packages
required_packages = ['yfinance', 'pandas', 'matplotlib', 'seaborn', 'plotly']	# Added plotly to the list of required packages

# Define the cache directory
CACHE_DIR = 'cache'

# Updated MARKETS dictionary

def load_markets(json_file='markets.json'):
    """Load markets and tickers from a JSON file."""
    try:
        with open(json_file, 'r') as file:
            markets = json.load(file)
        return markets
    except FileNotFoundError:
        print(f"Error: The file {json_file} was not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: The file {json_file} contains invalid JSON.")
        sys.exit(1)

# Load the MARKETS dictionary from the JSON file
MARKETS = load_markets()

def check_and_install(package):
    try:
        pkg_resources.get_distribution(package)
    except pkg_resources.DistributionNotFound:
        print(f"{package} is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"{package} has been installed.")

def install_pip_if_needed():
    try:
        import pip
    except ImportError:
        print("pip is not installed. Installing pip...")
        subprocess.check_call([sys.executable, "-m", "ensurepip"])
        print("pip has been installed.")

def install_packages():
    """Install required packages if not already installed."""
    installed_packages = {pkg.key for pkg in pkg_resources.working_set}
    missing_packages = set(required_packages) - installed_packages
    if missing_packages:
        print(f"Installing missing packages: {', '.join(missing_packages)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages])
    else:
        print("All required packages are already installed.")

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
    import yfinance as yf
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    import plotly.express as px  # Import Plotly inside the function to avoid unnecessary dependency if not used

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
    import matplotlib.pyplot as plt

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

def sns_plot_data(data, tickers, start_date, end_date):
    import yfinance as yf
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set(style="whitegrid")  # Set Seaborn style for better aesthetics
    plt.figure(figsize=(14, 8))
    
    # Define color palette
    palette = sns.color_palette("tab10", n_colors=len(tickers)*4)  # Enough colors for multiple lines
    color_idx = 0  # Index to keep track of colors
    
    for ticker in tickers:
        if ticker not in data:
            print(f"Skipping {ticker} as no data was downloaded.")
            continue
        stock_data = data[ticker]
        if stock_data.empty:
            print(f"No data to plot for {ticker}.")
            continue
        
        # Calculate Moving Averages
        stock_data['MA20'] = stock_data['Close'].rolling(window=20).mean()
        stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()
        
        # Melt the DataFrame for Seaborn
        plot_df = stock_data[['Open', 'Close', 'MA20', 'MA50']].reset_index().melt(id_vars='Date', var_name='Metric', value_name='Price')
        plot_df['Ticker'] = ticker  # Add ticker for hue
        
        # Plot each metric with different styles
        sns.lineplot(data=plot_df, x='Date', y='Price', hue='Metric', style='Metric',
                     markers=False, dashes=False, linewidth=1.5, palette=[palette[color_idx], palette[color_idx+1], palette[color_idx+2], palette[color_idx+3]])
        
        color_idx += 4  # Increment color index for next ticker
    
    plt.title('Stock Opening & Closing Prices with Moving Averages', fontsize=16)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Price ($)', fontsize=14)
    plt.legend(title='Metric', fontsize=10, title_fontsize=12)
    plt.tight_layout()
    
    # Save the plot as an image
    # Create a safe filename by replacing special characters
    safe_tickers = "_".join(tickers).replace("/", "_")
    filename = f"stock_plot_{safe_tickers}_{start_date}_to_{end_date}.png"
    plt.savefig(filename)
    print(f"\nPlot saved as {filename}")
    
    # Display the plot
    plt.show()

def plot_data_facets(data, tickers, start_date, end_date):
    # import yfinance as yf
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    # import plotly.express as px  # Import Plotly inside the function to avoid unnecessary dependency if not used

    sns.set(style="whitegrid")
    
    # Create a combined DataFrame
    combined_df = pd.DataFrame()
    for ticker in tickers:
        if ticker not in data or data[ticker].empty:
            print(f"Skipping {ticker} as no data was downloaded or data is empty.")
            continue
        stock_data = data[ticker].copy()
        stock_data.reset_index(inplace=True)
        stock_data['Ticker'] = ticker
        stock_data['MA20'] = stock_data['Close'].rolling(window=20).mean()
        stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()
        combined_df = pd.concat([combined_df, stock_data], ignore_index=True)
    
    # Melt the DataFrame for Seaborn
    melted_df = combined_df.melt(id_vars=['Date', 'Ticker'], value_vars=['Open', 'Close', 'MA20', 'MA50'],
                                 var_name='Metric', value_name='Price')
    
    # Create a FacetGrid
    g = sns.FacetGrid(melted_df, col="Ticker", hue="Metric", height=5, aspect=1.5, palette="tab10")
    g.map(sns.lineplot, "Date", "Price")
    g.add_legend()
    
    plt.subplots_adjust(top=0.9)
    g.fig.suptitle('Stock Opening & Closing Prices with Moving Averages')
    
    # Save the plot
    safe_tickers = "_".join(tickers).replace("/", "_")
    filename = f"stock_plot_facets_{safe_tickers}_{start_date}_to_{end_date}.png"
    plt.savefig(filename)
    print(f"\nFacet plot saved as {filename}")
    plt.show()

def plot_data_interactive(data, tickers, start_date, end_date):
    # import yfinance as yf
    import pandas as pd
    # import matplotlib.pyplot as plt
    # import seaborn as sns
    import plotly.express as px  # Import Plotly inside the function to avoid unnecessary dependency if not used

    combined_df = pd.DataFrame()
    for ticker in tickers:
        if ticker not in data or data[ticker].empty:
            print(f"Skipping {ticker} as no data was downloaded or data is empty.")
            continue
        stock_data = data[ticker].copy()
        stock_data.reset_index(inplace=True)
        stock_data['Ticker'] = ticker
        stock_data['MA20'] = stock_data['Close'].rolling(window=20).mean()
        stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()
        combined_df = pd.concat([combined_df, stock_data], ignore_index=True)
    
    # Melt the DataFrame for Plotly
    melted_df = combined_df.melt(id_vars=['Date', 'Ticker'], value_vars=['Open', 'Close', 'MA20', 'MA50'],
                                 var_name='Metric', value_name='Price')
    
    fig = px.line(melted_df, x='Date', y='Price', color='Metric', line_dash='Metric',
                  facet_col='Ticker', title='Stock Opening & Closing Prices with Moving Averages',
                  labels={'Price': 'Price ($)', 'Date': 'Date'}, hover_data=['Ticker'])
    
    fig.update_layout(legend_title_text='Metric', height=600)
    
    # Save the plot
    safe_tickers = "_".join(tickers).replace("/", "_")
    filename = f"stock_plot_interactive_{safe_tickers}_{start_date}_to_{end_date}.html"
    fig.write_html(filename)
    print(f"\nInteractive plot saved as {filename}")
    
    fig.show()

def main():
    print("=== Stock Data Analyzer ===")

    # Install packages
    install_packages()
    print("All required packages have been checked and installed.")

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
    
    print('Kindly enter choice of plot: \n1. Plot Data \n2. Seaborn Plot Data \n3. Plot Data Facets \n4. Plot Data Interactive')

    choice = int(input())
    
    # Call the appropriate function based on the user's choice
    if choice == 1:
        plot_data(data, selected_tickers, start_date, end_date)
    elif choice == 2:
        sns_plot_data(data, selected_tickers, start_date, end_date)
    elif choice == 3:
        plot_data_facets(data, selected_tickers, start_date, end_date)
    elif choice == 4:
        plot_data_interactive(data, selected_tickers, start_date, end_date)
    else:
        print("Invalid choice. Seems like we`ll go with the default plot, MatplotLib.")
        plot_data(data, selected_tickers, start_date, end_date)
    # Step 6: Plot data
    

    # sns_plot_data(data, selected_tickers, start_date, end_date)
    # Optional: Plot Facets
    # plot_data_facets(data, selected_tickers, start_date, end_date)
    
    # Optional: Interactive Plot using Plotly
    # plot_data_interactive(data, selected_tickers, start_date, end_date)

if __name__ == "__main__":
    main()
