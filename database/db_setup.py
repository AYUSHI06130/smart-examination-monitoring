import sqlite3
import os

# ==========================================
# Create Database Folder
# ==========================================

os.makedirs("database", exist_ok=True)

DATABASE_PATH = "database/monitoring.db"

connection = sqlite3.connect(DATABASE_PATH)

cursor = connection.cursor()

# ==========================================
# Candidate Table
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS Candidate(

    candidate_id TEXT PRIMARY KEY,

    name TEXT NOT NULL,

    email TEXT UNIQUE NOT NULL,

    password TEXT NOT NULL,

    photo_path TEXT

)
""")

# ==========================================
# Session Table
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS Session(

    session_id INTEGER PRIMARY KEY AUTOINCREMENT,

    candidate_id TEXT NOT NULL,

    start_time TEXT,

    end_time TEXT,

    status TEXT,

    paused_at TEXT,

    total_pause_seconds INTEGER DEFAULT 0,

    face_absence_duration INTEGER DEFAULT 0

    FOREIGN KEY(candidate_id)
    REFERENCES Candidate(candidate_id)

)
""")

# ==================================================
# Event Log Table
# ==================================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS EventLog(

    event_id INTEGER PRIMARY KEY AUTOINCREMENT,

    candidate_id TEXT NOT NULL,

    session_id INTEGER NOT NULL,

    event_type TEXT NOT NULL,

    timestamp TEXT NOT NULL,

    remarks TEXT,

    screenshot_path TEXT,

    FOREIGN KEY(candidate_id)
    REFERENCES Candidate(candidate_id)

)

""")

print("===================================")
print("Database Created Successfully")
print("===================================")

# ==========================================
# Monitoring Status Table
# ==========================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS MonitoringStatus(

    candidate_id TEXT PRIMARY KEY,

    face_status TEXT,

    face_absence_count INTEGER,

    browser_status TEXT,

    browser_focus_loss_count INTEGER,

    last_updated TEXT

)

""")

cursor.execute("""

CREATE TABLE IF NOT EXISTS IntegrityScore(

    score_id INTEGER PRIMARY KEY AUTOINCREMENT,

    candidate_id TEXT NOT NULL,

    session_id INTEGER NOT NULL,

    current_score INTEGER DEFAULT 100,

    final_score INTEGER,

    risk_level TEXT,

    total_events INTEGER DEFAULT 0,

    calculated_at TEXT,

    UNIQUE(candidate_id, session_id)

)
""")

connection.commit()

connection.close()

