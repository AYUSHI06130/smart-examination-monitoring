import sqlite3
from datetime import datetime
from config import DATABASE
import pandas as pd

# Penalty for each suspicious event
PENALTIES = {
    "Face Not Detected": 5,
    "Browser Focus Lost": 10,
    "Browser Tab Changed": 10,
    "Long Face Absence": 15,
    "Multiple Face Absence": 20,
    "Camera Blocked": 15,
    "Multiple Faces Detected": 20
}


def calculate_integrity_score(candidate_id, session_id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    
    df = pd.read_sql_query(
        """
        SELECT event_type
        FROM EventLog
        WHERE candidate_id=?
        AND session_id=?
        """,
        conn,
        params=(candidate_id, session_id)
    )


    # Face absence count
    cursor.execute("""
    SELECT face_absence_count
    FROM MonitoringStatus
    WHERE candidate_id=?
    """, (candidate_id,))

    row = cursor.fetchone()

    face_absence_count = row[0] if row else 0

    cursor.execute("""
    SELECT COUNT(*)
    FROM EventLog
    WHERE candidate_id=?
    AND session_id=?
    AND event_type='Browser Focus Lost'
    """, (candidate_id, session_id))

    browser_loss_count = cursor.fetchone()[0]

    # ------------------------------------
    # Get Session Duration
    # ------------------------------------

    cursor.execute("""
    SELECT
        start_time,
        end_time,
        face_absence_duration
    FROM Session
    WHERE session_id=?
    """,
    (session_id,))

    session_data = cursor.fetchone()

    start_time = datetime.strptime(
        session_data[0],
        "%Y-%m-%d %H:%M:%S"
    )

    end_time = datetime.strptime(
        session_data[1],
        "%Y-%m-%d %H:%M:%S"
    )


    absence_duration = session_data[2]

    total_seconds = int(
        (end_time - start_time).total_seconds()
    )

    if total_seconds > 0:

        face_presence_ratio = round(

            (
                (total_seconds - absence_duration)
                / total_seconds

            ) * 100,

            2

        )

    else:

        face_presence_ratio = 100

    score = 100

    event_weights = PENALTIES.copy()

    df["deduction"] = (
        df["event_type"]
          .map(event_weights)
          .fillna(0)
    )
   

    total_deduction = df["deduction"].sum()

    score -= total_deduction

    score = max(0, min(score, 100))

    total_events = len(df)

    if score >= 90:
        risk = "Excellent"

    elif score >= 75:
        risk = "Low Risk"

    elif score >= 50:
        risk = "Medium Risk"

    elif score >= 25:
        risk = "High Risk"

    else:
        risk = "Very High Risk"

    # ------------------------------------
    # Check if score already exists
    # ------------------------------------

    cursor.execute("""
    SELECT 1
    FROM IntegrityScore
    WHERE candidate_id=?
    AND session_id=?
    """,
    (
        candidate_id,
        session_id
    ))

    exists = cursor.fetchone()

    # ------------------------------------
    # Update if exists
    # ------------------------------------

    if exists:

        cursor.execute("""
        UPDATE IntegrityScore
        SET
            final_score=?,
            risk_level=?,
            total_events=?,
            calculated_at=?
        WHERE candidate_id=?
        AND session_id=?
        """,
        (
            score,
            risk,
            total_events,
            datetime.now(),
            candidate_id,
            session_id
        ))

    # ------------------------------------
    # Otherwise Insert
    # ------------------------------------

    else:

        cursor.execute("""
        INSERT INTO IntegrityScore
        (
            candidate_id,
            session_id,
            final_score,
            risk_level,
            total_events,
            calculated_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            candidate_id,
            session_id,
            score,
            risk,
            total_events,
            datetime.now()
        ))

    conn.commit()
    conn.close()

    return {
        "score": score,
        "risk": risk,
        "face_absence_count": face_absence_count,
        "browser_loss_count": browser_loss_count,
        "face_presence_ratio": face_presence_ratio,
        "total_events": total_events
    }

# ======================================================
# Live Integrity Score Update
# ======================================================

def update_integrity_score(candidate_id, penalty):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # ----------------------------------------
    # Get Latest Session
    # ----------------------------------------

    cursor.execute("""
        SELECT session_id
        FROM Session
        WHERE candidate_id=?
        ORDER BY session_id DESC
        LIMIT 1
    """, (candidate_id,))

    row = cursor.fetchone()

    if row is None:
        conn.close()
        return

    session_id = row[0]

    # ----------------------------------------
    # Get Current Score
    # ----------------------------------------

    cursor.execute("""
        SELECT
            current_score,
            total_events
        FROM IntegrityScore
        WHERE
            candidate_id=?
        AND
            session_id=?
    """,
    (
        candidate_id,
        session_id
    ))

    result = cursor.fetchone()

    if result is None:
        conn.close()
        return

    current_score = result[0]
    total_events = result[1]

    # ----------------------------------------
    # Deduct Marks
    # ----------------------------------------

    new_score = max(0, current_score - penalty)

    total_events += 1

    # ----------------------------------------
    # Risk Level
    # ----------------------------------------

    if new_score >= 90:
        risk = "Excellent"

    elif new_score >= 75:
        risk = "Low Risk"

    elif new_score >= 50:
        risk = "Medium Risk"

    elif new_score >= 25:
        risk = "High Risk"

    else:
        risk = "Very High Risk"

    # ----------------------------------------
    # Update Database
    # ----------------------------------------

    cursor.execute("""
        UPDATE IntegrityScore

        SET

            current_score=?,

            risk_level=?,

            total_events=?,

            calculated_at=?

        WHERE

            candidate_id=?

        AND

            session_id=?
    """,
    (
        new_score,
        risk,
        total_events,
        datetime.now(),
        candidate_id,
        session_id
    ))

    conn.commit()
    conn.close()

    print(f"Live Score Updated : {new_score}")    