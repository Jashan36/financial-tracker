from datetime import datetime
from typing import Optional, List, Dict
import sqlite3
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Simple database manager for SQLite operations"""
    
    def __init__(self, db_path: str = "financial_tracker.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create users table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    settings TEXT DEFAULT '{}'
                )
                ''')
                
                # Create transactions table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_session_id TEXT NOT NULL,
                    date DATE NOT NULL,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    confidence_score REAL DEFAULT 0.0,
                    type TEXT NOT NULL,
                    file_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_session_id) REFERENCES users (session_id)
                )
                ''')
                
                # Create analysis_results table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_session_id TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,
                    results TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_session_id) REFERENCES users (session_id)
                )
                ''')
                
                # Create custom_categories table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS custom_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_session_id TEXT NOT NULL,
                    category_name TEXT NOT NULL,
                    keywords TEXT NOT NULL,
                    emoji TEXT DEFAULT '📦',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_session_id) REFERENCES users (session_id)
                )
                ''')
                
                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_session ON transactions(user_session_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_session ON analysis_results(user_session_id)')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def create_or_update_user(self, session_id: str, settings: Dict = None):
        """Create or update user session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                settings_json = json.dumps(settings or {})
                
                cursor.execute('''
                INSERT OR REPLACE INTO users (session_id, settings, last_active)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (session_id, settings_json))
                
                conn.commit()
                logger.info(f"User session created/updated: {session_id}")
                
        except sqlite3.Error as e:
            logger.error(f"Error creating/updating user: {e}")
            raise
    
    def save_transactions(self, session_id: str, transactions: List[Dict], file_hash: str = None):
        """Save transactions to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Clear existing transactions for this session and file hash
                if file_hash:
                    cursor.execute('''
                    DELETE FROM transactions 
                    WHERE user_session_id = ? AND file_hash = ?
                    ''', (session_id, file_hash))
                
                # Insert new transactions
                for transaction in transactions:
                    cursor.execute('''
                    INSERT INTO transactions 
                    (user_session_id, date, description, amount, category, confidence_score, type, file_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        session_id,
                        transaction.get('date'),
                        transaction.get('description'),
                        transaction.get('amount'),
                        transaction.get('category'),
                        transaction.get('confidence_score', 0.0),
                        transaction.get('type'),
                        file_hash
                    ))
                
                conn.commit()
                logger.info(f"Saved {len(transactions)} transactions for session {session_id}")
                
        except sqlite3.Error as e:
            logger.error(f"Error saving transactions: {e}")
            raise
    
    def get_transactions(self, session_id: str, limit: int = None) -> List[Dict]:
        """Get transactions for a user session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = '''
                SELECT date, description, amount, category, confidence_score, type, created_at
                FROM transactions 
                WHERE user_session_id = ?
                ORDER BY date DESC
                '''
                
                params = [session_id]
                if limit:
                    query += ' LIMIT ?'
                    params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                transactions = []
                for row in rows:
                    transactions.append({
                        'date': row[0],
                        'description': row[1],
                        'amount': row[2],
                        'category': row[3],
                        'confidence_score': row[4],
                        'type': row[5],
                        'created_at': row[6]
                    })
                
                return transactions
                
        except sqlite3.Error as e:
            logger.error(f"Error getting transactions: {e}")
            return []
    
    def save_analysis_result(self, session_id: str, analysis_type: str, results: Dict):
        """Save analysis results"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                results_json = json.dumps(results)
                
                cursor.execute('''
                INSERT INTO analysis_results (user_session_id, analysis_type, results)
                VALUES (?, ?, ?)
                ''', (session_id, analysis_type, results_json))
                
                conn.commit()
                logger.info(f"Saved {analysis_type} analysis for session {session_id}")
                
        except sqlite3.Error as e:
            logger.error(f"Error saving analysis results: {e}")
            raise
    
    def add_custom_category(self, session_id: str, category_name: str, keywords: List[str], emoji: str = '📦'):
        """Add custom category for user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                keywords_json = json.dumps(keywords)
                
                cursor.execute('''
                INSERT INTO custom_categories (user_session_id, category_name, keywords, emoji)
                VALUES (?, ?, ?, ?)
                ''', (session_id, category_name, keywords_json, emoji))
                
                conn.commit()
                logger.info(f"Added custom category '{category_name}' for session {session_id}")
                
        except sqlite3.Error as e:
            logger.error(f"Error adding custom category: {e}")
            raise
    
    def get_custom_categories(self, session_id: str) -> Dict[str, Dict]:
        """Get custom categories for user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                SELECT category_name, keywords, emoji
                FROM custom_categories 
                WHERE user_session_id = ?
                ''', (session_id,))
                
                rows = cursor.fetchall()
                
                custom_categories = {}
                for row in rows:
                    category_name = row[0]
                    keywords = json.loads(row[1])
                    emoji = row[2]
                    
                    custom_categories[category_name] = {
                        'keywords': keywords,
                        'emoji': emoji,
                        'patterns': []  # Could be extended
                    }
                
                return custom_categories
                
        except sqlite3.Error as e:
            logger.error(f"Error getting custom categories: {e}")
            return {}
    
    def get_user_statistics(self, session_id: str) -> Dict:
        """Get user usage statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get transaction count
                cursor.execute('''
                SELECT COUNT(*) FROM transactions WHERE user_session_id = ?
                ''', (session_id,))
                transaction_count = cursor.fetchone()[0]
                
                # Get analysis count
                cursor.execute('''
                SELECT COUNT(*) FROM analysis_results WHERE user_session_id = ?
                ''', (session_id,))
                analysis_count = cursor.fetchone()[0]
                
                # Get first and last activity
                cursor.execute('''
                SELECT MIN(created_at), MAX(created_at) 
                FROM transactions 
                WHERE user_session_id = ?
                ''', (session_id,))
                activity = cursor.fetchone()
                
                return {
                    'transaction_count': transaction_count,
                    'analysis_count': analysis_count,
                    'first_activity': activity[0] if activity[0] else None,
                    'last_activity': activity[1] if activity[1] else None
                }
                
        except sqlite3.Error as e:
            logger.error(f"Error getting user statistics: {e}")
            return {}
    
    def cleanup_old_data(self, days_old: int = 30):
        """Clean up old data to manage storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete old transactions
                cursor.execute('''
                DELETE FROM transactions 
                WHERE created_at < datetime('now', '-{} days')
                '''.format(days_old))
                
                # Delete old analysis results
                cursor.execute('''
                DELETE FROM analysis_results 
                WHERE created_at < datetime('now', '-{} days')
                '''.format(days_old))
                
                conn.commit()
                logger.info(f"Cleaned up data older than {days_old} days")
                
        except sqlite3.Error as e:
            logger.error(f"Error cleaning up old data: {e}")

# Global database instance
db_manager = DatabaseManager()
