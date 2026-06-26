import sqlite3
import json
import os
import time

DB_PATH = os.path.join(os.path.dirname(__file__), "jobs.db")

class QueueManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # evaluation_queue: stores raw URLs to be scraped and evaluated
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS evaluation_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # review_queue: stores job details that passed evaluation and need manual review
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS review_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    output_dir TEXT NOT NULL,
                    email TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def push_evaluation(self, url: str) -> bool:
        """Pushes a URL to the evaluation queue. Returns True if inserted, False if already exists."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO evaluation_queue (url) VALUES (?)', (url,))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            # URL already exists (UNIQUE constraint)
            return False

    def pop_evaluation(self):
        """Pops a URL from the evaluation queue. Returns (id, url) or None."""
        with sqlite3.connect(self.db_path, isolation_level='EXCLUSIVE') as conn:
            cursor = conn.cursor()
            # Start a transaction to grab the oldest pending job
            cursor.execute('''
                SELECT id, url FROM evaluation_queue 
                WHERE status = 'pending' 
                ORDER BY created_at ASC LIMIT 1
            ''')
            row = cursor.fetchone()
            if row:
                job_id, url = row
                cursor.execute('UPDATE evaluation_queue SET status = ? WHERE id = ?', ('processing', job_id))
                conn.commit()
                return job_id, url
            return None

    def mark_evaluation_done(self, job_id, status='completed'):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE evaluation_queue SET status = ? WHERE id = ?', (status, job_id))
            conn.commit()

    def push_review(self, company_name: str, url: str, output_dir: str, email: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO review_queue (company_name, url, output_dir, email) 
                VALUES (?, ?, ?, ?)
            ''', (company_name, url, output_dir, email))
            conn.commit()

    def pop_review(self):
        with sqlite3.connect(self.db_path, isolation_level='EXCLUSIVE') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, company_name, url, output_dir, email FROM review_queue 
                WHERE status = 'pending' 
                ORDER BY created_at ASC LIMIT 1
            ''')
            row = cursor.fetchone()
            if row:
                job_id, company_name, url, output_dir, email = row
                cursor.execute('UPDATE review_queue SET status = ? WHERE id = ?', ('processing', job_id))
                conn.commit()
                return {
                    'id': job_id,
                    'company_name': company_name,
                    'url': url,
                    'output_dir': output_dir,
                    'email': email
                }
            return None

    def mark_review_done(self, job_id, status='completed'):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE review_queue SET status = ? WHERE id = ?', (status, job_id))
            conn.commit()
