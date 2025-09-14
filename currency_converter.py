#!/usr/bin/env python3
"""
Currency Converter Service for Financial Tracker
Handles currency conversion with live exchange rates and caching
"""

import requests
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
# Cache functionality removed - using simple in-memory cache instead
import pandas as pd

logger = logging.getLogger(__name__)

@dataclass
class ExchangeRate:
    """Data class for exchange rate information"""
    from_currency: str
    to_currency: str
    rate: float
    timestamp: datetime
    source: str

class CurrencyConverter:
    """Currency conversion service with live exchange rate fetching"""
    
    def __init__(self, cache=None):
        # Simple in-memory cache instead of Flask-Caching
        self.cache = {} if cache is None else cache
        self.cache_timeout = 3600  # 1 hour
        self.base_url = "https://api.exchangerate.host"
        self.fallback_rates = {
            # Common exchange rates (updated periodically)
            'USD': 1.0,
            'EUR': 0.85,
            'GBP': 0.73,
            'INR': 83.0,
            'JPY': 110.0,
            'CAD': 1.25,
            'AUD': 1.35,
            'CHF': 0.92,
            'SEK': 8.5,
            'NOK': 8.8,
            'DKK': 6.3,
            'PLN': 3.9,
            'CZK': 21.5,
            'HUF': 300.0,
            'RUB': 95.0,
            'BRL': 5.0,
            'MXN': 20.0,
            'ARS': 350.0,
            'CLP': 800.0,
            'COP': 4000.0,
            'PEN': 3.7,
            'UYU': 40.0,
            'VES': 36.0,
            'CNY': 7.2,
            'KRW': 1300.0,
            'THB': 35.0,
            'VND': 24000.0,
            'IDR': 15000.0,
            'MYR': 4.2,
            'SGD': 1.35,
            'HKD': 7.8,
            'TWD': 30.0,
            'NZD': 1.45,
            'PHP': 55.0,
            'ZAR': 18.0,
            'EGP': 30.0,
            'MAD': 10.0,
            'NGN': 750.0,
            'KES': 130.0,
            'GHS': 6.0,
            'TZS': 2300.0,
            'UGX': 3700.0,
            'RWF': 1200.0,
            'ETB': 55.0,
            'TRY': 30.0,
            'ILS': 3.7,
            'AED': 3.67,
            'SAR': 3.75,
            'QAR': 3.64,
            'KWD': 0.31,
            'BHD': 0.38,
            'OMR': 0.38,
            'JOD': 0.71,
            'LBP': 15000.0,
            'PKR': 280.0,
            'LKR': 320.0,
            'NPR': 133.0,
            'BDT': 110.0,
            'MMK': 2100.0,
            'LAK': 17000.0,
            'KHR': 4100.0,
            'MOP': 8.0,
            'BND': 1.35,
            'FJD': 2.2,
            'PGK': 3.7,
            'SBD': 8.3,
            'TOP': 2.3,
            'VUV': 120.0,
            'WST': 2.7,
            'XPF': 110.0,
            'AOA': 830.0,
            'BWP': 13.5,
            'LSL': 18.0,
            'SZL': 18.0,
            'ZMW': 18.0,
            'BIF': 2900.0,
            'DJF': 178.0,
            'ERN': 15.0,
            'SOS': 570.0,
            'SSP': 600.0,
            'SYP': 13000.0,
            'YER': 250.0,
            'AFN': 70.0,
            'AMD': 400.0,
            'AZN': 1.7,
            'GEL': 2.7,
            'KGS': 89.0,
            'KZT': 450.0,
            'MDL': 18.0,
            'TJS': 10.9,
            'TMT': 3.5,
            'UZS': 12000.0,
            'UAH': 36.0,
            'BYN': 3.2,
            'MKD': 56.0,
            'RSD': 108.0,
            'BAM': 1.8,
            'BGN': 1.8,
            'HRK': 6.7,
            'RON': 4.6,
            'ALL': 95.0,
            'ISK': 135.0,
            'MGA': 4500.0,
            'MUR': 45.0,
            'SCR': 13.5,
            'SLL': 18000.0,
            'LRD': 190.0,
            'CDF': 2500.0,
            'XAF': 600.0,
            'XOF': 600.0,
            'KMF': 450.0,
            'STN': 22.5,
            'MZN': 64.0,
            'NAD': 18.0,
            'ZWL': 360.0,
            'BMD': 1.0,
            'BSD': 1.0,
            'BBD': 2.0,
            'BZD': 2.0,
            'XCD': 2.7,
            'DOP': 56.0,
            'GTQ': 7.8,
            'HNL': 24.7,
            'JMD': 155.0,
            'NIO': 36.8,
            'PYG': 7200.0,
            'SRD': 38.0,
            'TTD': 6.8,
            'XDR': 0.75
        }
    
    def get_exchange_rate(self, from_currency: str, to_currency: str, use_cache: bool = True) -> float:
        """Get exchange rate between two currencies"""
        if from_currency == to_currency:
            return 1.0
        
        # Try cache first
        if use_cache and self.cache:
            cache_key = f"exchange_rate_{from_currency}_{to_currency}"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                # Check if cache is still valid (not expired)
                if time.time() - cached_data['timestamp'] < self.cache_timeout:
                    logger.debug(f"Using cached exchange rate: {from_currency} -> {to_currency} = {cached_data['rate']}")
                    return cached_data['rate']
                else:
                    # Remove expired cache entry
                    del self.cache[cache_key]
        
        # Try to fetch live rate
        try:
            rate = self._fetch_live_rate(from_currency, to_currency)
            if rate:
                # Cache the rate for 1 hour
                if self.cache:
                    cache_key = f"exchange_rate_{from_currency}_{to_currency}"
                    self.cache[cache_key] = {
                        'rate': rate,
                        'timestamp': time.time()
                    }
                logger.info(f"Fetched live exchange rate: {from_currency} -> {to_currency} = {rate}")
                return rate
        except Exception as e:
            logger.warning(f"Failed to fetch live rate for {from_currency} -> {to_currency}: {e}")
        
        # Fallback to static rates
        rate = self._get_fallback_rate(from_currency, to_currency)
        logger.warning(f"Using fallback exchange rate: {from_currency} -> {to_currency} = {rate}")
        return rate
    
    def _fetch_live_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Fetch live exchange rate from API"""
        try:
            url = f"{self.base_url}/convert"
            params = {
                'from': from_currency.upper(),
                'to': to_currency.upper(),
                'amount': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('success') and 'result' in data:
                return float(data['result'])
            
            logger.warning(f"API response indicates failure: {data}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {from_currency} -> {to_currency}: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Failed to parse API response for {from_currency} -> {to_currency}: {e}")
            return None
    
    def _get_fallback_rate(self, from_currency: str, to_currency: str) -> float:
        """Get fallback exchange rate"""
        from_rate = self.fallback_rates.get(from_currency.upper(), 1.0)
        to_rate = self.fallback_rates.get(to_currency.upper(), 1.0)
        
        # Convert through USD
        if from_currency.upper() == 'USD':
            return to_rate
        elif to_currency.upper() == 'USD':
            return 1.0 / from_rate
        else:
            # Convert from_currency -> USD -> to_currency
            usd_rate = 1.0 / from_rate
            return usd_rate * to_rate
    
    def convert_amount(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Convert amount from one currency to another"""
        if from_currency == to_currency:
            return amount
        
        rate = self.get_exchange_rate(from_currency, to_currency)
        converted_amount = amount * rate
        
        logger.debug(f"Converted {amount} {from_currency} to {converted_amount:.4f} {to_currency} (rate: {rate})")
        return converted_amount
    
    def get_supported_currencies(self) -> List[str]:
        """Get list of supported currencies"""
        return list(self.fallback_rates.keys())
    
    def convert_transactions(self, transactions: List[Dict], target_currency: str = 'USD') -> List[Dict]:
        """Convert a list of transactions to target currency"""
        if not transactions:
            return []
        
        converted_transactions = []
        conversion_stats = {}
        
        for transaction in transactions:
            original_currency = transaction.get('currency', 'USD')
            
            if original_currency == target_currency:
                # No conversion needed
                converted_transaction = transaction.copy()
                converted_transaction['original_currency'] = original_currency
                converted_transaction['conversion_rate'] = 1.0
            else:
                # Convert to target currency
                original_amount = transaction.get('amount', 0)
                conversion_rate = self.get_exchange_rate(original_currency, target_currency)
                converted_amount = self.convert_amount(original_amount, original_currency, target_currency)
                
                converted_transaction = transaction.copy()
                converted_transaction['amount'] = converted_amount
                converted_transaction['original_amount'] = original_amount
                converted_transaction['original_currency'] = original_currency
                converted_transaction['conversion_rate'] = conversion_rate
            
            converted_transaction['display_currency'] = target_currency
            converted_transactions.append(converted_transaction)
            
            # Track conversion stats
            key = f"{original_currency} -> {target_currency}"
            if key not in conversion_stats:
                conversion_stats[key] = {'count': 0, 'total_original': 0, 'total_converted': 0}
            conversion_stats[key]['count'] += 1
            conversion_stats[key]['total_original'] += abs(original_amount)
            conversion_stats[key]['total_converted'] += abs(converted_amount)
        
        logger.info(f"Converted {len(transactions)} transactions to {target_currency}")
        for key, stats in conversion_stats.items():
            logger.info(f"  {key}: {stats['count']} transactions, "
                       f"{stats['total_original']:.2f} -> {stats['total_converted']:.2f}")
        
        return converted_transactions
    
    def convert_dataframe(self, df: pd.DataFrame, target_currency: str = 'USD', 
                         amount_column: str = 'amount', currency_column: str = 'currency') -> pd.DataFrame:
        """Convert a DataFrame of transactions to target currency"""
        if df.empty:
            return df
        
        converted_df = df.copy()
        
        # Add conversion columns
        converted_df['original_amount'] = converted_df[amount_column]
        converted_df['original_currency'] = converted_df[currency_column]
        converted_df['display_currency'] = target_currency
        
        # Convert amounts
        for idx, row in converted_df.iterrows():
            original_currency = row[currency_column]
            original_amount = row[amount_column]
            
            if original_currency != target_currency:
                conversion_rate = self.get_exchange_rate(original_currency, target_currency)
                converted_amount = self.convert_amount(original_amount, original_currency, target_currency)
                converted_df.at[idx, amount_column] = converted_amount
                converted_df.at[idx, 'conversion_rate'] = conversion_rate
            else:
                converted_df.at[idx, 'conversion_rate'] = 1.0
        
        return converted_df
    
    def get_conversion_summary(self, transactions: List[Dict], target_currency: str = 'USD') -> Dict:
        """Get summary of currency conversions"""
        if not transactions:
            return {}
        
        currency_counts = {}
        currency_totals = {}
        conversion_rates = {}
        
        for transaction in transactions:
            original_currency = transaction.get('currency', 'USD')
            amount = abs(transaction.get('amount', 0))
            
            currency_counts[original_currency] = currency_counts.get(original_currency, 0) + 1
            currency_totals[original_currency] = currency_totals.get(original_currency, 0) + amount
            
            if original_currency != target_currency:
                rate = self.get_exchange_rate(original_currency, target_currency)
                conversion_rates[original_currency] = rate
        
        return {
            'target_currency': target_currency,
            'currencies_found': list(currency_counts.keys()),
            'currency_counts': currency_counts,
            'currency_totals': currency_totals,
            'conversion_rates': conversion_rates,
            'total_transactions': len(transactions)
        }
