import sqlite3
import hashlib
from modules.database import get_db_connection

class AuthModule:
    def __init__(self):
        self.db_path = "db/users.db"
        self.setup_database()
    
    def setup_database(self):
        """Create users database and default admin user if not exists"""
        conn = get_db_connection("users.db")
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
        
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username, password):
        """Authenticate user"""
        conn = get_db_connection("users.db")
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        
        result = cursor.fetchone()
        
        return result is not None
    
    def create_user(self, username, password, creator):
        """Create a new user"""
        try:
            conn = get_db_connection("users.db")
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            
            # Log the action
            self.log_action(creator, "CREATE_USER", f"Created user: {username}")
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Username already exists
    
    def delete_user(self, username, requester):
        """Delete a user (users can only delete themselves)"""
        conn = get_db_connection("users.db")
        cursor = conn.cursor()
        
        # Check if user can be deleted (not admin)
        cursor.execute("SELECT can_delete FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if result and result[0] == 1 and username == requester:
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            self.log_action(requester, "DELETE_USER", f"Deleted user: {username}")
            conn.commit()
            return True
        else:
            return False
    
    def get_all_users(self):
        """Get all users"""
        conn = get_db_connection("users.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT username, created_at FROM users")
        users = cursor.fetchall()
        
        return users
    
    def log_action(self, user, action, details=""):
        """Log user actions"""
        conn = get_db_connection("users.db")
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO logs (user, action, details) VALUES (?, ?, ?)",
            (user, action, details)
        )
        
        conn.commit()
    
    def get_logs(self):
        """Get all logs"""
        conn = get_db_connection("users.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT user, action, timestamp, details FROM logs ORDER BY timestamp DESC")
        logs = cursor.fetchall()
        
        return logs