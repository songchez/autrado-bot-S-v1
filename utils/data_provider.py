import yfinance as yf
import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

class DataProvider:
    MARKET_SUFFIXES = {
        'US': '',
        'KRX': '.KS',
        'KOSDAQ': '.KQ'
    }
    
    POPULAR_KRX_TICKERS = {
        '005930': 'Samsung Electronics',
        '000660': 'SK Hynix',
        '035420': 'NAVER',
        '051910': 'LG Chem',
        '035720': 'Kakao',
        '003670': 'Posco Holdings'
    }
    
    @classmethod
    def detect_market(cls, ticker: str) -> str:
        if ticker.endswith('.KS') or ticker.endswith('.KQ'):
            return 'KRX'
        elif ticker.isdigit() and len(ticker) == 6:
            return 'KRX'
        else:
            return 'US'
    
    @classmethod
    def normalize_ticker(cls, ticker: str, market: Optional[str] = None) -> str:
        base_ticker = ticker.upper()
        for suffix in ['.KS', '.KQ']:
            if base_ticker.endswith(suffix):
                base_ticker = base_ticker[:-3]
                break
        
        if market is None:
            market = cls.detect_market(ticker)
        
        if market == 'KRX':
            if base_ticker.isdigit():
                return f"{base_ticker}.KS"
            else:
                return f"{base_ticker}.KS"
        else:
            return base_ticker
    
    @classmethod
    def get_market_info(cls, ticker: str) -> Dict[str, str]:
        market = cls.detect_market(ticker)
        normalized_ticker = cls.normalize_ticker(ticker, market)
        
        info = {
            'original_ticker': ticker,
            'normalized_ticker': normalized_ticker,
            'market': market,
            'exchange': 'KRX' if market == 'KRX' else 'NASDAQ/NYSE',
            'currency': 'KRW' if market == 'KRX' else 'USD',
            'timezone': 'Asia/Seoul' if market == 'KRX' else 'America/New_York'
        }
        
        if market == 'KRX' and ticker.replace('.KS', '').replace('.KQ', '') in cls.POPULAR_KRX_TICKERS:
            base_ticker = ticker.replace('.KS', '').replace('.KQ', '')
            info['korean_name'] = cls.POPULAR_KRX_TICKERS[base_ticker]
        
        return info
    
    @classmethod
    def download_data(cls, ticker: str, start: Optional[date] = None, end: Optional[date] = None, period: str = "1y", interval: str = "1d", market: Optional[str] = None, progress: bool = False) -> Optional[pd.DataFrame]:
        try:
            normalized_ticker = cls.normalize_ticker(ticker, market)
            market_info = cls.get_market_info(ticker)
            
            logger.info(f"Downloading data for {normalized_ticker} ({market_info['market']} market)")
            
            if start and end:
                data = yf.download(normalized_ticker, start=start, end=end, interval=interval, progress=progress)
            else:
                data = yf.download(normalized_ticker, period=period, interval=interval, progress=progress)
            
            if data.empty:
                logger.error(f"No data returned for {normalized_ticker}")
                return None
            
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)
            
            data.attrs['market_info'] = market_info
            
            logger.info(f"Successfully downloaded {len(data)} rows for {normalized_ticker}")
            return data
            
        except Exception as e:
            logger.error(f"Error downloading data for {ticker}: {e}")
            return None
    
    @classmethod
    def validate_ticker(cls, ticker: str, market: Optional[str] = None) -> bool:
        try:
            normalized_ticker = cls.normalize_ticker(ticker, market)
            test_data = yf.download(normalized_ticker, period="5d", progress=False)
            return not test_data.empty
        except Exception as e:
            logger.error(f"Ticker validation failed for {ticker}: {e}")
            return False
    
    @classmethod
    def get_ticker_suggestions(cls, query: str, market: str = 'ALL') -> List[Dict[str, str]]:
        suggestions = []
        
        if market in ['ALL', 'KRX']:
            query_lower = query.lower()
            for ticker_code, name in cls.POPULAR_KRX_TICKERS.items():
                if (query_lower in name.lower() or query in ticker_code or query_lower in name.lower().replace(' ', '')):
                    suggestions.append({
                        'ticker': f"{ticker_code}.KS",
                        'name': name,
                        'market': 'KRX',
                        'display': f"{ticker_code}.KS - {name}"
                    })
        
        if market in ['ALL', 'US']:
            popular_us = {
                'AAPL': 'Apple Inc.',
                'GOOGL': 'Alphabet Inc.',
                'MSFT': 'Microsoft Corporation',
                'AMZN': 'Amazon.com Inc.',
                'TSLA': 'Tesla Inc.'
            }
            
            query_upper = query.upper()
            for ticker, name in popular_us.items():
                if (query_upper in ticker or query.lower() in name.lower()):
                    suggestions.append({
                        'ticker': ticker,
                        'name': name,
                        'market': 'US',
                        'display': f"{ticker} - {name}"
                    })
        
        return suggestions[:10]