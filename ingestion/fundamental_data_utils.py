import logging
import pandas as pd
import yfinance as yf
from nseconnect import Nse
from typing import Optional, Dict, Any
from datetime import datetime

class FundamentalDataUtils:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.nse = Nse()

    def get_index_constituents(self, index_name):
        """
        Get a list of stocks that are part of a specified index.
        """
        try:
            return self.nse.get_stocks_in_index(index=index_name)
        except Exception as e:
            self.logger.error(f"Unable to get stocks in index {index_name}: {e}")
            return []

    def get_fundamentals_overview(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch basic fundamental data for a given NSE stock using Yahoo Finance.

        Args:
            symbol (str): NSE symbol (e.g., 'INFY', 'TCS')

        Returns:
            dict or None: Fundamental data or None if error
        """
        yf_symbol = f"{symbol}.NS"
        try:
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            self.logger.info(f"Fetched fundamentals for {symbol} from Yahoo Finance.")

            return {
                "symbol": symbol,
                "name": info.get("longName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "marketCap": info.get("marketCap"),
                "peRatio": info.get("trailingPE"),
                "eps": info.get("trailingEps"),
                "bookValue": info.get("bookValue"),
                "priceToBook": info.get("priceToBook"),
                "dividendYield": info.get("dividendYield"),
                "returnOnEquity": info.get("returnOnEquity"),
                "debtToEquity": info.get("debtToEquity"),
                "profitMargins": info.get("profitMargins"),
                "operatingMargins": info.get("operatingMargins")
            }

        except Exception as e:
            self.logger.error(f"Error fetching fundamental data for {symbol}: {e}")
            return None

    def filter_recent_years(self, df, years):
        """Filter a DataFrame to only include data from the last `years`."""
        if df.empty:
            return df
        df.index = pd.to_datetime(df.index)
        cutoff_year = datetime.now().year - years
        return df[df.index.year >= cutoff_year]

    def get_detailed_fundamentals(self, symbol :str, years: int =5, frequency:str = 'annually'):
        """
        Fetch fundamental data (financial statements) for an NSE-listed stock.

        Args:
            ticker_symbol (str): NSE ticker symbol (e.g. 'RELIANCE.NS').
            years (int): Number of previous years of data to fetch.

        Returns:
            pd.DataFrame: Combined dataframe of income statement, balance sheet, and cashflow.
        """
        yf_symbol = f"{symbol}.NS"
        try:
            ticker = yf.Ticker(yf_symbol)

            # Select statement based on frequency
            if frequency == 'annual':
                income_stmt = ticker.financials
                balance_sheet = ticker.balance_sheet
                cash_flow = ticker.cashflow
            elif frequency == 'quarterly':
                income_stmt = ticker.quarterly_financials
                balance_sheet = ticker.quarterly_balance_sheet
                cash_flow = ticker.quarterly_cashflow
            else:
                raise ValueError("Frequency must either be 'annual' or 'quarterly'")

            # Transpose
            income_stmt = income_stmt.T
            balance_sheet = balance_sheet.T
            cash_flow = cash_flow.T

            # Convert index to datetime
            income_stmt.index = pd.to_datetime(income_stmt.index)
            balance_sheet.index = pd.to_datetime(balance_sheet.index)
            cash_flow.index = pd.to_datetime(cash_flow.index)

            # Filter for last `years` only
            cutoff_date = datetime.now().replace(month=1, day=1)
            cutoff_year = cutoff_date.year - years
            income_stmt = income_stmt[income_stmt.index.year >= cutoff_year]
            balance_sheet = balance_sheet[balance_sheet.index.year >= cutoff_year]
            cash_flow = cash_flow[cash_flow.index.year >= cutoff_year]

            # Combine all dataframes
            combined_df = pd.concat(
                [income_stmt.add_prefix('IS_'),
                balance_sheet.add_prefix('BS_'),
                cash_flow.add_prefix('CF_')],
                axis=1
            )
            combined_df['Symbol'] = symbol
            combined_df['Frequency'] = frequency.capitalize()
            
            combined_df.reset_index(inplace=True)
            combined_df.rename(columns={'index': 'Date'}, inplace=True)

            return combined_df
        
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()

    def is_valid_symbol(self, symbol: str) -> bool:
        """
        Check if a stock symbol exists in NSE.

        Args:
            symbol (str): NSE stock symbol

        Returns:
            bool: True if valid, else False
        """
        try:
            symbols = self.nse.get_stock_codes()
            is_valid = symbol.upper() in symbols
            self.logger.info(f"{'Valid' if is_valid else 'Invalid'} symbol: {symbol}")
            return is_valid
        except Exception as e:
            self.logger.error(f"Failed to validate symbol '{symbol}': {e}")
            return False
