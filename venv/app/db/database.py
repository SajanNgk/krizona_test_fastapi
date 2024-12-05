import mysql.connector
from app.core.config import settings

db = mysql.connector.connect(
    host=settings.DB_HOST,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    database=settings.DATABASE_NAME
)

cursor = db.cursor()