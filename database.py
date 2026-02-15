import mysql.connector
from mysql.connector import Error
from config import Config

class Database:
    def __init__(self):
        self.initialize_database()

    def initialize_database(self):
        """Create database and tables once"""
        try:
            conn = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD
            )

            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}")
            conn.database = Config.DB_NAME

            # Events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    date DATE NOT NULL,
                    location VARCHAR(255),
                    type VARCHAR(100),
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)

            # Generated posts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS generated_posts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    event_id INT NOT NULL,
                    platform VARCHAR(50) NOT NULL,
                    tone VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    hashtags TEXT,
                    status VARCHAR(20) DEFAULT 'draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
                )
            """)

            conn.commit()
            cursor.close()
            conn.close()

            print("Database initialized successfully")

        except Error as e:
            print("Database initialization error:", e)

    def get_connection(self):
        """Always return a fresh connection"""
        try:
            return mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME
            )
        except Error as e:
            print("Connection error:", e)
            return None