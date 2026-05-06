import os
import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self):
        self.initialize_database()

    def initialize_database(self):
        try:
            conn = mysql.connector.connect(
                host=os.environ.get("MYSQLHOST"),
                user=os.environ.get("MYSQLUSER"),
                password=os.environ.get("MYSQLPASSWORD"),
                port=os.environ.get("MYSQLPORT")
            )

            cursor = conn.cursor()

            db_name = os.environ.get("MYSQLDATABASE")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            conn.database = db_name

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
        try:
            return mysql.connector.connect(
                host=os.environ.get("MYSQLHOST"),
                user=os.environ.get("MYSQLUSER"),
                password=os.environ.get("MYSQLPASSWORD"),
                database=os.environ.get("MYSQLDATABASE"),
                port=os.environ.get("MYSQLPORT")
            )
        except Error as e:
            print("Connection error:", e)
            return None