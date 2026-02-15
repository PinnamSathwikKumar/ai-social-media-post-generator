"""
Database setup script
This script helps initialize the database and tables
"""
import os
from database import Database
from config import Config

if __name__ == '__main__':
    print("Setting up database...")
    print(f"Connecting to: {Config.DB_HOST}/{Config.DB_NAME}")
    print(f"User: {Config.DB_USER}")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("\n⚠ Warning: .env file not found!")
        print("Please copy env_template.txt to .env and configure your database settings.")
        print("\nYou can still proceed, but make sure MySQL is running and accessible.")
    
    db = Database()
    
    if db.connection and db.connection.is_connected():
        print("\n✓ Database connection successful!")
        print("✓ Tables created/verified successfully!")
        print("\nYou can now run the application with: python app.py")
    else:
        print("\n✗ Failed to connect to database.")
        print("\nTroubleshooting steps:")
        print("1. Make sure MySQL server is running")
        print("2. Check your .env file configuration:")
        print("   - DB_HOST (default: localhost)")
        print("   - DB_USER (default: root)")
        print("   - DB_PASSWORD (your MySQL password)")
        print("   - DB_NAME (default: social_media_generator)")
        print("3. Verify MySQL is accessible on the configured host and port")
    
    db.close()

