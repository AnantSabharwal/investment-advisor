# import os
# import pandas as pd
# from datetime import datetime
# from fundamental_data_utils import FundamentalDataUtils  # Make sure this file exists
# import time

# def collect_fundamental_data():
#     print("📊 Welcome to Fundamental Data Collector for NSE Stocks")

#     # Ask user for index and save mode
#     index_name = input("Enter the NSE index name (e.g., NIFTY 50): ").strip().upper()
#     data_type = input("📂 Type of data — 'overview' or 'detailed': ").strip().lower()
    
#     if data_type not in ['overview', 'detailed']:
#         print("❌ Invalid data type. Choose either 'overview' or 'detailed'.")
#         return

#     if data_type == 'detailed':
#         frequency = input("⏱ Frequency — 'annual' or 'quarterly': ").strip().lower()
#         if frequency not in ['annual', 'quarterly']:
#             print("❌ Invalid frequency. Choose 'annual' or 'quarterly'.")
#             return
#         try:
#             years = int(input("📅 Number of years of data to fetch (e.g., 5): ").strip())
#         except ValueError:
#             print("❌ Invalid year input. Must be a number.")
#             return
#     else:
#         frequency = None
#         years = None


#     save_mode = input("💾 Save mode — type 'individual' for separate files, or 'combined' for one CSV: ").strip().lower()

#     if save_mode not in ['individual', 'combined']:
#         print("❌ Invalid choice. Please enter 'individual' or 'combined'.")
#         return

#     collector = FundamentalDataUtils()

#     print(f"\n🔍 Fetching constituents for index: {index_name}")
#     constituents = collector.get_index_constituents(index_name)

#     if not constituents:
#         print(f"❌ No stocks found for index: {index_name}. Please check the name.")
#         return

#     # Output path setup
#     output_dir = os.path.join("data","raw" ,"fundamental", index_name.replace(" ", "_"))
#     os.makedirs(output_dir, exist_ok=True)

#     today = datetime.today().strftime('%Y-%m-%d')
#     combined_data = []

#     for symbol in constituents:
#         print(f"📈 Fetching fundamental data for {symbol}...")
#         data = collector.get_fundamentals_yfinance(symbol)

#         if data:
#             df = pd.DataFrame([data])

#             if save_mode == 'individual':
#                 filename = f"{symbol}_{today}.csv"
#                 filepath = os.path.join(output_dir, filename)
#                 df.to_csv(filepath, index=False)
#                 print(f"✅ Saved {symbol} fundamentals to {filepath}")

#             combined_data.append(df)
#         else:
#             print(f"⚠️ Skipping {symbol}: No data found.")

#         time.sleep(0.5)  # Be nice to the data source

#     # Handle combined file saving
#     if save_mode == 'combined' and combined_data:
#         final_df = pd.concat(combined_data, ignore_index=True)
#         combined_filename = f"fundamental_data_{index_name.replace(' ', '_')}_{today}.csv"
#         combined_filepath = os.path.join(output_dir, combined_filename)
#         final_df.to_csv(combined_filepath, index=False)
#         print(f"\n📦 Combined fundamentals saved to: {combined_filepath}")
#     elif save_mode == 'combined' and not combined_data:
#         print("❌ No data collected to combine.")
#     elif save_mode == 'individual':
#         print(f"\n📁 All individual fundamental files saved in: {output_dir}")

# if __name__ == "__main__":
#     collect_fundamental_data()
import os
import time
import pandas as pd
from datetime import datetime
from fundamental_data_utils import FundamentalDataUtils


def collect_fundamental_data():
    print("📊 Welcome to Fundamental Data Collector for NSE Stocks")

    # Step 1: User Inputs
    index_name = input("Enter the NSE index name (e.g., NIFTY 50): ").strip().upper()

    print("\n📋 Choose data type:")
    print("1. Overview (Basic data from Yahoo Finance)")
    print("2. Detailed (Financial statements)")
    data_choice = input("Enter 1 or 2: ").strip()

    if data_choice not in ['1', '2']:
        print("❌ Invalid choice. Please enter 1 or 2.")
        return

    if data_choice == '2':
        frequency = input("⏱ Frequency — type 'annual' or 'quarterly': ").strip().lower()
        if frequency not in ['annual', 'quarterly']:
            print("❌ Invalid frequency. Please enter 'annual' or 'quarterly'.")
            return
        try:
            years = int(input("📆 Number of years of data to fetch: ").strip())
        except ValueError:
            print("❌ Invalid number of years.")
            return

    save_mode = input("\n💾 Save mode — type 'individual' for separate files, or 'combined' for one CSV: ").strip().lower()
    if save_mode not in ['individual', 'combined']:
        print("❌ Invalid choice. Please enter 'individual' or 'combined'.")
        return

    # Step 2: Get Constituents
    collector = FundamentalDataUtils()
    print(f"\n🔍 Fetching constituents for index: {index_name}...")
    constituents = collector.get_index_constituents(index_name)

    if not constituents:
        print(f"❌ No stocks found for index: {index_name}. Please check the name.")
        return

    # Step 3: Setup output
    output_dir = os.path.join("data", "raw", "fundamental", index_name.replace(" ", "_"))
    os.makedirs(output_dir, exist_ok=True)
    today = datetime.today().strftime('%Y-%m-%d')
    combined_data = []

    # Step 4: Loop through each symbol
    for symbol in constituents:
        if not collector.is_valid_symbol(symbol):
            print(f"⚠️ Skipping {symbol}: Invalid NSE symbol.")
            continue

        print(f"📈 Fetching data for {symbol}...")

        try:
            if data_choice == '1':
                data = collector.get_fundamentals_overview(symbol)
                if data:
                    df = pd.DataFrame([data])
                else:
                    print(f"⚠️ Skipping {symbol}: No overview data found.")
                    continue
            else:
                df = collector.get_detailed_fundamentals(symbol, years=years, frequency=frequency)
                if df.empty:
                    print(f"⚠️ Skipping {symbol}: No detailed data found.")
                    continue

            # Step 5: Save the data
            if save_mode == 'individual':
                filename = f"{symbol}_{today}.csv"
                filepath = os.path.join(output_dir, filename)
                df.to_csv(filepath, index=False)
                print(f"✅ Saved {symbol} data to {filepath}")

            combined_data.append(df)

        except Exception as e:
            print(f"❌ Error processing {symbol}: {e}")

        time.sleep(0.5)  # Respect data source rate limits

    # Step 6: Save combined file
    if save_mode == 'combined' and combined_data:
        final_df = pd.concat(combined_data, ignore_index=True)
        suffix = "overview" if data_choice == '1' else f"{frequency}_{years}yrs"
        combined_filename = f"fundamental_data_{index_name.replace(' ', '_')}_{suffix}_{today}.csv"
        combined_filepath = os.path.join(output_dir, combined_filename)
        final_df.to_csv(combined_filepath, index=False)
        print(f"\n📦 Combined data saved to: {combined_filepath}")
    elif save_mode == 'combined':
        print("❌ No data collected to combine.")
    elif save_mode == 'individual':
        print(f"\n📁 All individual files saved in: {output_dir}")


if __name__ == "__main__":
    collect_fundamental_data()
