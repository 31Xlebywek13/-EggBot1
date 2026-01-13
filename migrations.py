import sqlite3

DB_PATH = "egg.db"


def table_exists(cur, table):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None


def column_exists(cur, table, column):
    cur.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cur.fetchall())


def safe_add_column(cur, table, column, definition):
    if not column_exists(cur, table, column):
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        print(f"[MIGRATION] Добавлено поле {table}.{column}")


def run_migrations():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("[MIGRATIONS] Запуск миграций...")

    # --- USERS TABLE ---
    if table_exists(cur, "users"):

        safe_add_column(cur, "users", "last_meditation", "TEXT DEFAULT NULL")
        safe_add_column(cur, "users", "last_daily", "TEXT DEFAULT NULL")
        safe_add_column(cur, "users", "daily_streak", "INTEGER DEFAULT 0")
        safe_add_column(cur, "users", "stars", "INTEGER DEFAULT 0")
        safe_add_column(cur, "users", "items", "TEXT DEFAULT ''")
        safe_add_column(cur, "users", "court_votes", "INTEGER DEFAULT 0")
        safe_add_column(cur, "users", "court_accused", "INTEGER DEFAULT 0")

    else:
        print("[MIGRATIONS] Таблица users не найдена — миграции пропущены.")

    conn.commit()
    conn.close()

    print("[MIGRATIONS] Завершено.")
