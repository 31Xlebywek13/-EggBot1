import sqlite3
from datetime import date

conn = sqlite3.connect("egg.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("DATABASE.PY LOADED")


# ======================
# ИНИЦИАЛИЗАЦИЯ ТАБЛИЦ
# ======================

def init_db():
    # Пользователи
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            vibrations INTEGER DEFAULT 100,
            donated INTEGER DEFAULT 0,
            rank TEXT DEFAULT '🥚 Послушник',

            -- Новые поля
            last_meditation TEXT DEFAULT NULL,
            last_daily TEXT DEFAULT NULL,
            daily_streak INTEGER DEFAULT 0,
            stars INTEGER DEFAULT 0,
            items TEXT DEFAULT '',

            court_votes INTEGER DEFAULT 0,
            court_accused INTEGER DEFAULT 0
        )
    """)

    # Пожертвования
    cur.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            anonymous INTEGER,
            day TEXT
        )
    """)

    # Судебные дела
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            case_id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            message_id INTEGER,
            accused_id INTEGER,
            status TEXT
        )
    """)

    # Голоса суда
    cur.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            case_id INTEGER,
            user_id INTEGER,
            vote TEXT
        )
    """)

    conn.commit()


# ======================
# ПОЛЬЗОВАТЕЛИ
# ======================

def add_user(user_id: int, username: str | None):
    cur.execute(
        "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
        (user_id, username or "")
    )
    conn.commit()


def get_user(user_id: int):
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cur.fetchone()


def add_vibrations(user_id: int, amount: int):
    cur.execute(
        "UPDATE users SET vibrations = vibrations + ? WHERE user_id=?",
        (amount, user_id)
    )
    conn.commit()


def remove_vibrations(user_id: int, amount: int):
    cur.execute(
        "UPDATE users SET vibrations = vibrations - ? WHERE user_id=? AND vibrations >= ?",
        (amount, user_id, amount)
    )
    conn.commit()


# ======================
# ПОЖЕРТВОВАНИЯ
# ======================

def donate(user_id: int, amount: int, anonymous: bool):
    today = date.today().isoformat()

    cur.execute(
        "UPDATE users SET vibrations = vibrations - ?, donated = donated + ? WHERE user_id=?",
        (amount, amount, user_id)
    )

    cur.execute(
        "INSERT INTO donations (user_id, amount, anonymous, day) VALUES (?, ?, ?, ?)",
        (user_id, amount, int(anonymous), today)
    )

    conn.commit()


def top_donators(limit=5):
    cur.execute("""
        SELECT username, donated
        FROM users
        ORDER BY donated DESC
        LIMIT ?
    """, (limit,))
    return cur.fetchall()


def daily_stats():
    today = date.today().isoformat()
    cur.execute("""
        SELECT SUM(amount) FROM donations WHERE day=?
    """, (today,))
    return cur.fetchone()[0] or 0


# ======================
# СУД
# ======================

def create_case(chat_id, message_id, accused_id):
    cur.execute("""
        INSERT INTO cases (chat_id, message_id, accused_id, status)
        VALUES (?, ?, ?, 'open')
    """, (chat_id, message_id, accused_id))
    conn.commit()
    return cur.lastrowid


def add_vote(case_id, user_id, vote):
    cur.execute(
        "DELETE FROM votes WHERE case_id=? AND user_id=?",
        (case_id, user_id)
    )
    cur.execute(
        "INSERT INTO votes (case_id, user_id, vote) VALUES (?, ?, ?)",
        (case_id, user_id, vote)
    )
    conn.commit()


def count_votes(case_id):
    cur.execute("""
        SELECT vote, COUNT(*) as count
        FROM votes
        WHERE case_id=?
        GROUP BY vote
    """, (case_id,))
    return {row["vote"]: row["count"] for row in cur.fetchall()}


def get_case(case_id):
    cur.execute("""
        SELECT chat_id, accused_id
        FROM cases
        WHERE case_id=? AND status='open'
    """, (case_id,))
    return cur.fetchone()


def close_case(case_id):
    cur.execute(
        "UPDATE cases SET status='closed' WHERE case_id=?",
        (case_id,)
    )
    conn.commit()


# ======================
# РАНГИ (РУЧНЫЕ)
# ======================

def set_rank(user_id: int, rank: str):
    cur.execute(
        "UPDATE users SET rank=? WHERE user_id=?",
        (rank, user_id)
    )
    conn.commit()


# ======================
# ПРОФИЛЬ (АЛИАС)
# ======================

def get_profile(user_id: int):
    return get_user(user_id)
