#!/usr/bin/env python3
"""
System-wide Unicode logging fix for Windows
This must be imported before any other modules to fix logging issues
"""

import sys
import io
import logging
import locale

def setup_unicode_logging():
    """Fix Unicode logging issues system-wide"""
    
    # Force UTF-8 for all streams on Windows
    if sys.platform == 'win32':
        try:
            # Reconfigure stdout and stderr
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, 
                encoding='utf-8', 
                errors='replace'
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, 
                encoding='utf-8', 
                errors='replace'
            )
            
            # Set locale for Unicode support
            try:
                locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
            except:
                try:
                    locale.setlocale(locale.LC_ALL, 'C.UTF-8')
                except:
                    pass  # Continue without locale setting
            
        except Exception as e:
            print(f"Warning: Could not fully configure Unicode logging: {e}")
    
    # Reconfigure all existing logging handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        try:
            if hasattr(handler, 'stream') and hasattr(handler.stream, 'buffer'):
                handler.stream = io.TextIOWrapper(
                    handler.stream.buffer, 
                    encoding='utf-8', 
                    errors='replace'
                )
        except Exception:
            pass  # Continue if handler can't be reconfigured

def create_safe_logger(name):
    """Create a logger that handles Unicode safely"""
    logger = logging.getLogger(name)
    
    # Add Unicode-safe handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        
        # Create formatter that handles Unicode
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger

# Apply the fix immediately when this module is imported
setup_unicode_logging()

# Create a safe logger for this module
logger = create_safe_logger(__name__)
logger.info("Unicode logging fix applied successfully")
