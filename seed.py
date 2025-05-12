"""
Script to seed the database with initial data
"""

import asyncio
from app.db.seed_data import seed_data

if __name__ == "__main__":
    asyncio.run(seed_data()) 