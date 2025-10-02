import os
import pandas as pd
from datetime import datetime
from technical_data_utils import TechnicalDataUtils;
from datetime import timedelta

def collect_technical_data():
    print("📊 Welcome to Technical Data Collector for NSE Stocks")
    
    default_start = datetime.today() - timedelta(days=5)
    default_end = datetime.today()

    index_name = input("Enter the NSE index name (e.g., NIFTY 50): ").strip().upper()
    start_raw = input(f"Enter start date (e.g., 01-01-2023) [Default: {default_start.strftime('%d-%m-%Y')}]: ").strip()
    end_raw = input(f"Enter end date (e.g., 31-12-2023) [Default: {default_end.strftime('%d-%m-%Y')}]: ").strip()
    
    save_mode = input("💾 Save mode — type 'individual' for separate files, or 'combined' for one CSV: ").strip().lower()

    if save_mode not in ['individual', 'combined']:
        print("❌ Invalid choice. Please enter 'individual' or 'combined'.")
        return

    collector = TechnicalDataUtils()
    
    try:
        start_date = collector.parse_date_to_standard(start_raw) if start_raw else default_start.strftime('%Y-%m-%d')
        end_date = collector.parse_date_to_standard(end_raw) if end_raw else default_end.strftime('%Y-%m-%d')
    except ValueError as ve:
        print(f"❌ Error parsing dates: {ve}")
        return

    print(f"\n🔍 Fetching constituents for index: {index_name}")
    constituents = collector.get_index_constituents(index_name)

    if not constituents:
        print(f"❌ No stocks found for index: {index_name}. Please check the name.")
        return

    # Create output directory structure
    output_dir = os.path.join("data", "raw", "technical", index_name.replace(" ", "_"))
    os.makedirs(output_dir, exist_ok=True)

    combined_data = []
    today = datetime.today().strftime('%Y-%m-%d')

    for symbol in constituents:
        print(f"⏳ Fetching historical data for {symbol}...")
        data = collector.get_historical_data(symbol, start_date, end_date)
        
        if data is not None and not data.empty:
            data.reset_index(inplace=True)
            
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            data['Symbol'] = symbol
            
            if save_mode == 'individual':
                filename = f"{symbol}_{today}.csv"
                filepath = os.path.join(output_dir, filename)
                data.to_csv(filepath, index=False, header=True)
                print(f"✅ Saved {symbol} data to {filepath}")

            combined_data.append(data)
        else:
            print(f"⚠️ Skipping {symbol}: No data found.")
    
    if save_mode == 'combined' and combined_data:
        combined_df = pd.concat(combined_data, ignore_index=True)
        combined_filename = f"technical_data_{index_name.replace(' ', '_')}_{today}.csv"
        combined_filepath = os.path.join(output_dir, combined_filename)
        combined_df.to_csv(combined_filepath, index=False)
        print(f"\n📦 Combined data saved to: {combined_filepath}")
    elif save_mode == 'combined' and not combined_data:
        print("❌ No data collected to combine.")
    elif save_mode == 'individual':
        print(f"\n📁 All individual files saved in: {output_dir}")

if __name__ == "__main__":
    collect_technical_data()
