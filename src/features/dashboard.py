"""
Progress Dashboard and Analytics module for AI Flashcard Generator
Tracks learning progress with SQLite database
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProgressDatabase:
    """
    SQLite database manager for storing quiz attempts and learning metrics.
    """
    
    DB_FILE = 'data/progress.db'
    
    def __init__(self):
        # Ensure data directory exists
        Path('data').mkdir(exist_ok=True)
        self.db_path = Path(self.DB_FILE)
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema if it doesn't exist."""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Quiz attempts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quiz_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    topic TEXT NOT NULL,
                    score_percentage REAL NOT NULL,
                    total_questions INTEGER NOT NULL,
                    correct_answers INTEGER NOT NULL,
                    incorrect_answers INTEGER NOT NULL,
                    time_taken_seconds INTEGER,
                    flashcards_used INTEGER
                )
            ''')
            
            # Global metrics table (singleton)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS global_metrics (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    total_flashcards_generated INTEGER DEFAULT 0,
                    total_quizzes_taken INTEGER DEFAULT 0,
                    highest_score REAL DEFAULT 0,
                    last_quiz_date TIMESTAMP
                )
            ''')
            
            # Ensure global metrics row exists
            cursor.execute('''
                INSERT OR IGNORE INTO global_metrics (id) VALUES (1)
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def save_quiz_attempt(
        self,
        topic: str,
        score_percentage: float,
        total_questions: int,
        correct_answers: int,
        incorrect_answers: int,
        time_taken_seconds: Optional[int] = None,
        flashcards_used: int = 0
    ) -> bool:
        """
        Save a quiz attempt to the database.
        
        Returns:
            True if successful, False otherwise
        """
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert quiz attempt
            cursor.execute('''
                INSERT INTO quiz_attempts 
                (topic, score_percentage, total_questions, correct_answers, incorrect_answers, time_taken_seconds, flashcards_used)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (topic, score_percentage, total_questions, correct_answers, incorrect_answers, time_taken_seconds, flashcards_used))
            
            # Update global metrics
            cursor.execute('''
                UPDATE global_metrics
                SET total_quizzes_taken = total_quizzes_taken + 1,
                    highest_score = MAX(highest_score, ?),
                    last_quiz_date = CURRENT_TIMESTAMP
                WHERE id = 1
            ''', (score_percentage,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Quiz attempt saved: {topic} - {score_percentage}%")
            return True
            
        except Exception as e:
            logger.error(f"Error saving quiz attempt: {e}")
            return False
    
    def get_all_quiz_attempts(self) -> List[Dict]:
        """Get all quiz attempts from database."""
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, date, topic, score_percentage, total_questions, 
                       correct_answers, incorrect_answers, time_taken_seconds
                FROM quiz_attempts
                ORDER BY date DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error fetching quiz attempts: {e}")
            return []
    
    def get_quiz_attempts_by_topic(self, topic: str) -> List[Dict]:
        """Get all quiz attempts for a specific topic."""
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT date, score_percentage, correct_answers, incorrect_answers
                FROM quiz_attempts
                WHERE topic = ?
                ORDER BY date DESC
            ''', (topic,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error fetching topic attempts: {e}")
            return []
    
    def get_global_metrics(self) -> Dict:
        """Get global cumulative metrics."""
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT total_flashcards_generated, total_quizzes_taken, 
                       highest_score, last_quiz_date
                FROM global_metrics
                WHERE id = 1
            ''')
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            else:
                return {
                    'total_flashcards_generated': 0,
                    'total_quizzes_taken': 0,
                    'highest_score': 0,
                    'last_quiz_date': None
                }
                
        except Exception as e:
            logger.error(f"Error fetching global metrics: {e}")
            return {}
    
    def update_flashcard_count(self, count: int):
        """Update the total flashcards generated count."""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE global_metrics
                SET total_flashcards_generated = total_flashcards_generated + ?
                WHERE id = 1
            ''', (count,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating flashcard count: {e}")
    
    def get_average_score(self) -> float:
        """Calculate average score from all quiz attempts."""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT AVG(score_percentage) FROM quiz_attempts')
            result = cursor.fetchone()
            conn.close()
            
            return round(result[0], 2) if result[0] else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating average score: {e}")
            return 0.0
    
    def get_learning_streak(self) -> int:
        """
        Calculate learning streak (consecutive days with quiz attempts).
        """
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all unique dates with quiz attempts, ordered by date DESC
            cursor.execute('''
                SELECT DISTINCT DATE(date) as quiz_date
                FROM quiz_attempts
                ORDER BY quiz_date DESC
            ''')
            
            dates = [row['quiz_date'] for row in cursor.fetchall()]
            conn.close()
            
            if not dates:
                return 0
            
            # Calculate streak
            streak = 0
            today = datetime.now().date()
            
            for i, date_str in enumerate(dates):
                quiz_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                expected_date = today - timedelta(days=i)
                
                # If dates match, increment streak
                if quiz_date == expected_date:
                    streak += 1
                else:
                    break
            
            return streak
            
        except Exception as e:
            logger.error(f"Error calculating streak: {e}")
            return 0
    
    def get_topic_statistics(self) -> Dict[str, Dict]:
        """Get statistics grouped by topic."""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT topic,
                       COUNT(*) as attempts,
                       AVG(score_percentage) as avg_score,
                       MAX(score_percentage) as best_score,
                       MIN(score_percentage) as worst_score
                FROM quiz_attempts
                GROUP BY topic
                ORDER BY topic
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            topic_stats = {}
            for row in results:
                topic_stats[row[0]] = {
                    'attempts': row[1],
                    'avg_score': round(row[2], 2),
                    'best_score': row[3],
                    'worst_score': row[4]
                }
            
            return topic_stats
            
        except Exception as e:
            logger.error(f"Error fetching topic statistics: {e}")
            return {}
    
    def get_score_trend_data(self, days: int = 30) -> List[Tuple]:
        """Get score trend data for the last N days."""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(f'''
                SELECT DATE(date) as quiz_date, AVG(score_percentage) as avg_score
                FROM quiz_attempts
                WHERE date >= datetime('now', '-{days} days')
                GROUP BY DATE(date)
                ORDER BY quiz_date ASC
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error fetching trend data: {e}")
            return []
    
    def clear_all_data(self):
        """Clear all data from database (for reset/testing)."""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM quiz_attempts')
            cursor.execute('''
                UPDATE global_metrics
                SET total_flashcards_generated = 0,
                    total_quizzes_taken = 0,
                    highest_score = 0,
                    last_quiz_date = NULL
                WHERE id = 1
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Database cleared")
            
        except Exception as e:
            logger.error(f"Error clearing database: {e}")


def create_progress_database() -> ProgressDatabase:
    """Factory function to create progress database."""
    return ProgressDatabase()
