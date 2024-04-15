import os
import mysql.connector

db = mysql.connector.connect(
    host=os.getenv("DATABASE_HOST") or "localhost",
    user=os.getenv("DATABASE_USER"),
    password=os.getenv("DATABASE_PASSWORD"),
    database=os.getenv("DATABASE"),
    port=int(os.getenv("DATABASE_PORT") or 3306),
)

print("Database connected!" if db else "Database connection failed!")
