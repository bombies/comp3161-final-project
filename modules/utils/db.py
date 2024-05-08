import os
import mysql.connector

from modules.models.account import AccountType

db = mysql.connector.connect(
    host=os.getenv("DATABASE_HOST") or "localhost",
    user=os.getenv("DATABASE_USER"),
    password=os.getenv("DATABASE_PASSWORD"),
    database=os.getenv("DATABASE"),
    port=int(os.getenv("DATABASE_PORT") or 3306),
)

print("Database connected!" if db else "Database connection failed!")

if db:
    # Create the root user if it doesn't exist.
    db_cursor = db.cursor()
    db_cursor.execute("SELECT * FROM Account WHERE email = 'root'")
    if not db_cursor.fetchone():
        db_cursor.execute(
            "INSERT INTO Account (email, password, account_type, name) VALUES (%s, %s, %s, %s)",
            (
                "root",
                os.getenv("MASTER_PASSWORD"),
                AccountType.Admin.name,
                "Root User",
            ),
        )
        db.commit()
        print("Root user created!")
    else:
        print("Root user already exists, skipping creation!")
