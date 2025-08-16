import sqlite3
import hashlib
import os
from datetime import datetime

class AuthModule:
    def __init__(self):
        self.db_path = "db/users.db"
        self.current_user = None
        self.log_refresh_callback = None
        self.setup_database()
    
    def setup_database(self):
        """Create users database and default admin user if not exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                can_delete BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        ''')
        
        # Create default admin user if not exists
        cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
        if not cursor.fetchone():
            # Hash the default password
            password_hash = self.hash_password("admin123")
            cursor.execute(
                "INSERT INTO users (username, password_hash, can_delete) VALUES (?, ?, ?)",
                ("admin", password_hash, 0)
            )
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username, password):
        """Authenticate user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        
        result = cursor.fetchone()
        
        if result:
            self.current_user = username
            self.log_action(username, "LOGIN", "User logged in successfully", conn)
            conn.close()
            return True
        
        conn.close()
        return False
    
    def create_user(self, username, password, creator):
        """Create a new user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            password_hash = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            
            # Log the action
            self.log_action(creator, "CREATE_USER", f"Created user: {username}", conn)
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False  # Username already exists
    
    def delete_user(self, username, requester):
        """Delete a user (users can only delete themselves)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if user can be deleted (not admin)
        cursor.execute("SELECT can_delete FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if result and result[0] == 1 and username == requester:
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            self.log_action(requester, "DELETE_USER", f"Deleted user: {username}", conn)
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
    
    def get_all_users(self):
        """Get all users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT username, created_at FROM users")
        users = cursor.fetchall()
        
        conn.close()
        return users
    
    def set_log_refresh_callback(self, callback):
        """Set the callback function to refresh the audit log"""
        self.log_refresh_callback = callback

    def log_action(self, user, action, details="", conn=None):
        """Log user actions"""
        close_conn = False
        if conn is None:
            conn = sqlite3.connect(self.db_path)
            close_conn = True
        
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO logs (user, action, details) VALUES (?, ?, ?)",
            (user, action, details)
        )
        
        if close_conn:
            conn.commit()
            conn.close()

        if self.log_refresh_callback:
            self.log_refresh_callback()
    
    def get_logs(self, username=None):
        """Get logs for a specific user, or all logs if no user is specified."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if username:
            cursor.execute("SELECT user, action, timestamp, details FROM logs WHERE user = ? ORDER BY timestamp DESC", (username,))
        else:
            cursor.execute("SELECT user, action, timestamp, details FROM logs ORDER BY timestamp DESC")
        
        logs = cursor.fetchall()
        
        conn.close()
        return logs
