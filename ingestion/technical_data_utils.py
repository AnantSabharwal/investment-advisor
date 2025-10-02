import logging
from nseconnect import Nse
import yfinance as yf
from dateutil import parser

class TechnicalDataUtils:
    def __init__(self):
        # Setup logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.nse = Nse()

    def get_all_stock_symbols(self):
        """
        Fetch all stock symbols listed on NSE.
        """
        try:
            return self.nse.get_stock_codes()
        except Exception as e:
            self.logger.error(f"Error fetching stock codes: {e}")
            return {}

    def get_all_indices(self):
        """
        Retrieve a list of all NSE indices.
        """
        try:
            return self.nse.get_index_list()
        except Exception as e:
            self.logger.error(f"Error fetching index list: {e}")
            return []

    def get_index_constituents(self, index_name):
        """
        Get a list of stocks that are part of a specified index.
        """
        try:
            return self.nse.get_stocks_in_index(index=index_name)
        except Exception as e:
            self.logger.error(f"Unable to get stocks in index {index_name}: {e}")
            return []

    def get_live_data(self, symbol, all_data=False):
        """
        Fetch live quote for a given stock symbol.
        """
        try:
            return self.nse.get_quote(symbol, all_data=all_data)
        except Exception as e:
            self.logger.error(f"Cannot fetch data for symbol {symbol}: {e}")
            return None

    def is_valid_symbol(self, symbol):
        """
        Check if a symbol is valid on NSE.
        """
        symbols = self.get_all_stock_symbols()
        is_valid = symbol in symbols
        self.logger.info(f"{'Valid' if is_valid else 'Invalid'} symbol: {symbol}")
        return is_valid

    def get_historical_data(self, symbol, start_date, end_date, interval='1d'):
        """
        Get historical market data for a symbol using Yahoo Finance.
        """
        yf_symbol = f"{symbol}.NS"
        try:
            data = yf.download(yf_symbol, start=start_date, end=end_date, interval=interval)
            if data.empty:
                self.logger.warning(f"No historical data found for {symbol}")
                return None
            return data
        except Exception as e:
            self.logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None

    def parse_date_to_standard(self, date_str):
        """
        Convert a date string in various formats to 'YYYY-MM-DD'.
        Raises ValueError if parsing fails.
        """
        try:
            parsed_date = parser.parse(date_str)
            return parsed_date.strftime('%Y-%m-%d')
        except Exception as e:
            self.logger.error(f"Invalid date format: {date_str}. Error: {e}")
            raise ValueError(f"Could not parse date: {date_str}")