import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.database = os.getenv('DB_NAME', 'finance_tracker')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        
    def create_connection(self):
        """Create a database connection"""
        try:
            conn = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            return conn
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    def initialize_database(self):
        """Initialize the database with required tables"""
        conn = self.create_connection()
        if conn is None:
            return False
            
        try:
            cursor = conn.cursor()
            
            # Create categories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) UNIQUE NOT NULL,
                    type ENUM('income', 'expense') NOT NULL
                )
            """)
            
            # Create transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    amount DECIMAL(10, 2) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    type ENUM('income', 'expense') NOT NULL,
                    description TEXT,
                    date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create budgets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    category VARCHAR(50) NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    month VARCHAR(7) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert default categories if they don't exist
            default_categories = [
                ('Salary', 'income'),
                ('Freelance', 'income'),
                ('Investment', 'income'),
                ('Gift', 'income'),
                ('Other Income', 'income'),
                ('Food', 'expense'),
                ('Transportation', 'expense'),
                ('Entertainment', 'expense'),
                ('Utilities', 'expense'),
                ('Rent', 'expense'),
                ('Healthcare', 'expense'),
                ('Education', 'expense'),
                ('Shopping', 'expense'),
                ('Other Expense', 'expense')
            ]
            
            for name, type in default_categories:
                cursor.execute(
                    "INSERT IGNORE INTO categories (name, type) VALUES (%s, %s)",
                    (name, type)
                )
            
            conn.commit()
            return True
            
        except Error as e:
            print(f"Error initializing database: {e}")
            return False
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute a query and return results if fetch is True"""
        conn = self.create_connection()
        if conn is None:
            return None
            
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.lastrowid
            
            return result
        except Error as e:
            print(f"Error executing query: {e}")
            return None
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()