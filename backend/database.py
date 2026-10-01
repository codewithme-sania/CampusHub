import sqlite3
import os


# =========================================================
# CAMPUSHUB DATABASE
# Always use the main CampusHub database
# =========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE_NAME = os.path.join(
    BASE_DIR,
    "campushub.db"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    connection = sqlite3.connect(DATABASE_NAME)

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# CREATE TABLES
# =========================================================

def create_tables():

    connection = get_connection()

    try:

        # =====================================================
        # USERS
        # =====================================================

        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                college TEXT NOT NULL,
                password TEXT NOT NULL,
                branch TEXT,
                year TEXT,
                skills TEXT
            )
        """)

        user_columns = connection.execute(
            "PRAGMA table_info(users)"
        ).fetchall()

        user_column_names = [
            column["name"]
            for column in user_columns
        ]

        if "branch" not in user_column_names:
            connection.execute(
                "ALTER TABLE users ADD COLUMN branch TEXT"
            )

        if "year" not in user_column_names:
            connection.execute(
                "ALTER TABLE users ADD COLUMN year TEXT"
            )

        if "skills" not in user_column_names:
            connection.execute(
                "ALTER TABLE users ADD COLUMN skills TEXT"
            )


        # =====================================================
        # OPPORTUNITIES
        # =====================================================

        connection.execute("""
            CREATE TABLE IF NOT EXISTS opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                date TEXT NOT NULL,
                location TEXT NOT NULL,
                organizer TEXT NOT NULL,
                application_link TEXT
            )
        """)


        # =====================================================
        # EVENTS
        # =====================================================

        connection.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                date TEXT NOT NULL,
                location TEXT NOT NULL,
                organizer TEXT NOT NULL,
                registration_link TEXT
            )
        """)

        event_columns = connection.execute(
            "PRAGMA table_info(events)"
        ).fetchall()

        event_column_names = [
            column["name"]
            for column in event_columns
        ]

        if "registration_link" not in event_column_names:

            connection.execute(
                "ALTER TABLE events ADD COLUMN registration_link TEXT"
            )


        # =====================================================
        # SAVED OPPORTUNITIES
        # =====================================================

        connection.execute("""
            CREATE TABLE IF NOT EXISTS saved_opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                opportunity_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (opportunity_id) REFERENCES opportunities(id)
            )
        """)


        connection.commit()

        print("Database tables are ready.")

        print("Using database:")
        print(DATABASE_NAME)


    except Exception as e:

        print("Database error:", e)

    finally:

        connection.close()