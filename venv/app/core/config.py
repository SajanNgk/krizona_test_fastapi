# app/core/config.py

import os

class Settings:
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "krizona")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))

settings = Settings()
