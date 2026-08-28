from flask import Blueprint, render_template, redirect, url_for
from flask import send_from_directory
from flask import flash, session
from flask import request,jsonify,session
from flask import Response
import os
import cv2
import pandas as pd
import csv
import io

from utils.camera_manager import CameraManager

from utils.integrity_score import calculate_integrity_score, PENALTIES
from utils.integrity_score import update_integrity_score

import sqlite3
from datetime import datetime



#from config import DATABASE
from config import (
    DATABASE,
    ADMIN_USERNAME,
    ADMIN_PASSWORD
)
# ==========================================
# Blueprint
# ==========================================

exam = Blueprint("exam", __name__)

# ==========================================
# Camera Manager
# ==========================================

camera_manager = None


# ==========================================
# Helper Function
# ==========================================

def get_latest_session(candidate_id):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""

    SELECT
        session_id,
        status

    FROM Session

    WHERE candidate_id=?

    ORDER BY session_id DESC

    LIMIT 1

    """, (candidate_id,))

    latest = cursor.fetchone()

    connection.close()

    return latest


# ==========================================
# Save Browser Screenshot
# ==========================================

def save_browser_screenshot(candidate_id):

    global camera_manager

    if camera_manager is None:

        return None

    frame = camera_manager.get_current_frame()

    if frame is None:

        return None

    candidate_folder = os.path.join(

        "evidence",

        f"Candidate_{candidate_id}"

    )

    os.makedirs(candidate_folder, exist_ok=True)

    filename = (

        "browser_focus_lost_"

        + datetime.now().strftime("%H-%M-%S")

        + ".png"

    )

    filepath = os.path.join(

        candidate_folder,

        filename

    )

    cv2.imwrite(filepath, frame)

    return filepath    

# ==========================================
# Video Frame Generator
# ==========================================

def generate_frames():

    global camera_manager

    if camera_manager is None:
        return

    while True:

        latest = get_latest_session(camera_manager.candidate_id)

        if latest is None:
            break

        # Stop streaming only after exam has ended

        if latest[1] == "Ended":
            break

        frame = camera_manager.get_frame()

        if frame is None:
            break

        success, buffer = cv2.imencode(".jpg", frame)

        if not success:
            continue

        frame_bytes = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n'
            + frame_bytes +
            b'\r\n'
        )

    camera_manager.stop_camera()

# ==========================================
# Video Feed
# ==========================================

@exam.route("/video_feed")
def video_feed():

    return Response(

        generate_frames(),

        mimetype="multipart/x-mixed-replace; boundary=frame"

    )

# ==========================================
# Exam Page
# ==========================================

@exam.route("/exam")
def exam_page():

    if "candidate_id" not in session:

        flash("Please login first.")

        return redirect(url_for("auth.login"))

    latest = get_latest_session(session["candidate_id"])

    status = "Not Started"

    if latest:

        status = latest[1]

    return render_template(
    "exam.html",
    status=status,
    exam_ended=(status == "Ended"),
    name=session["name"],
    candidate_id=session["candidate_id"]
    )

    


# ==========================================
# Start Exam
# ==========================================

@exam.route("/start_exam")
def start_exam():
    print("========== START EXAM ROUTE CALLED ==========")

    if "candidate_id" not in session:

        flash("Please login first.")

        return redirect(url_for("auth.login"))

    candidate_id = session["candidate_id"]

    #new update---------
    global camera_manager

    camera_manager = CameraManager(candidate_id)
    print("CameraManager created")

    opened = camera_manager.start_camera()

    print("Camera opened:", opened)

    if not opened:

        flash("Unable to access webcam.")

        return redirect(url_for("exam.exam_page"))
    #---------------------    

    latest = get_latest_session(candidate_id)

    # --------------------------------------

    if latest:

        if latest[1] == "Running":

        

            return redirect(url_for("exam.exam_page"))

        if latest[1] == "Paused":

        

            return redirect(url_for("exam.exam_page"))

    # --------------------------------------

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""

    INSERT INTO Session

    (candidate_id,start_time,status)

    VALUES(?,?,?)

    """,

    (

        candidate_id,

        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "Running"

    ))

    # ------------------------------------------
    # Get newly created session id
    # ------------------------------------------

    session_id = cursor.lastrowid

    # ------------------------------------------
    # Initialize Integrity Score
    # ------------------------------------------

    cursor.execute("""
    INSERT INTO IntegrityScore
    (
        candidate_id,
        session_id,
        current_score,
        final_score,
        risk_level,
        total_events,
        calculated_at
    )

    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    (
        candidate_id,
        session_id,
        100,
        None,
        "Low",
        0,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    connection.commit()

    

    # Log Exam Started event
    cursor.execute("""
    INSERT INTO EventLog
    (
        candidate_id,
        session_id,
        event_type,
        timestamp,
        remarks
    )
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        candidate_id,
        session_id,
        "Exam Started",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Candidate started the exam"
    ))

    connection.commit()
    connection.close()

    

    return redirect(url_for("exam.exam_page"))

# ==========================================
# Log Browser Activity
# ==========================================

@exam.route("/log_browser_event", methods=["POST"])
def log_browser_event():

    candidate_id = session.get("candidate_id")
    

    if candidate_id is None:
        return jsonify({"status": "error"}), 401

    latest = get_latest_session(candidate_id)

    if latest is None:
        return jsonify({"status": "error", "message": "No active session"}), 400

    session_id = latest[0]    

    data = request.get_json()

    event_type = data["event_type"]
    remarks = data["remarks"]
    screenshot_path = save_browser_screenshot(candidate_id)
    # ------------------------------------------
    # Live Integrity Score Update
    # ------------------------------------------

    BROWSER_PENALTIES = {

        "Browser Focus Lost": 10,

        "Browser Tab Changed": 10,

        "Fullscreen Exited": 15,

        "Developer Tools Opened": 20

    }

    penalty = BROWSER_PENALTIES.get(event_type, 0)

    if penalty > 0:

        update_integrity_score(

            candidate_id,

            penalty

    )

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO EventLog
        (
            candidate_id,
            session_id,
            event_type,
            timestamp,
            remarks,
            screenshot_path
        )

        VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        candidate_id,
        session_id,
        event_type,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        remarks,
        screenshot_path
    ))

    connection.commit()
    connection.close()

    return jsonify({"status": "success"}) 


# ==========================================
# Pause / Resume
# ==========================================

@exam.route("/toggle_exam")
def toggle_exam():

    if "candidate_id" not in session:

        flash("Please login first.")
        return redirect(url_for("auth.login"))

    latest = get_latest_session(session["candidate_id"])

    if latest is None:

        flash("Start the exam first.")
        return redirect(url_for("exam.exam_page"))

    session_id = latest[0]
    status = latest[1]

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # ==========================================
    # Pause Exam
    # ==========================================

    if status == "Running":

        cursor.execute("""

            UPDATE Session

            SET
                status=?,
                paused_at=?

            WHERE session_id=?

        """,

        (

            "Paused",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            session_id

        ))

    

    # ==========================================
    # Resume Exam
    # ==========================================

    elif status == "Paused":

        cursor.execute("""

            SELECT
                paused_at,
                total_pause_seconds

            FROM Session

            WHERE session_id=?

        """,

        (

            session_id,

        ))

        data = cursor.fetchone()

        paused_at = data[0]
        total_pause = data[1]

        paused_time = datetime.strptime(
            paused_at,
            "%Y-%m-%d %H:%M:%S"
        )

        pause_duration = int(
            (datetime.now() - paused_time).total_seconds()
        )

        total_pause += pause_duration

        cursor.execute("""

            UPDATE Session

            SET
                status=?,
                paused_at=NULL,
                total_pause_seconds=?

            WHERE session_id=?

        """,

        (

            "Running",
            total_pause,
            session_id

        ))

        

    # ==========================================
    # Already Ended
    # ==========================================

    elif status == "Ended":

        
        connection.close()

        return redirect(url_for("exam.exam_page"))

    connection.commit()
    connection.close()

    return jsonify({"status": "success"})


# ==========================================
# End Exam
# ==========================================

@exam.route("/end_exam")
def end_exam():
    global camera_manager

    if "candidate_id" not in session:

        flash("Please login first.")

        return redirect(url_for("auth.login"))

    latest = get_latest_session(session["candidate_id"])

    if latest is None:

        

        return redirect(url_for("exam.exam_page"))

    session_id = latest[0]

    status = latest[1]

    if status == "Ended":

        

        return redirect(url_for("exam.exam_page"))

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""

    UPDATE Session

    SET

        end_time=?,

        status=?,

        face_absence_duration=?


    WHERE session_id=?

    """,

    (

        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "Ended",

        camera_manager.face_monitor.total_absence_duration,

        session_id

    ))

    connection.commit()

    connection.close()

    # ------------------------------------
    # Calculate Integrity Score
    # ------------------------------------

    candidate_id = session["candidate_id"]

    result = calculate_integrity_score(
        candidate_id,
        session_id
    )

    # ------------------------------------
    # Candidate Information
    # ------------------------------------

    candidate_name = session["name"]

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM EventLog
        WHERE candidate_id=?
        AND session_id=?
        AND event_type='Face Not Detected'
    """, (session["candidate_id"], session_id))

    face_absence_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM EventLog
        WHERE candidate_id=?
        AND session_id=?
        AND event_type='Browser Focus Lost'
    """, (session["candidate_id"], session_id))

    browser_loss_count = cursor.fetchone()[0]

    # Total Suspicious Events
    cursor.execute("""
    SELECT COUNT(*)
    FROM EventLog
    WHERE candidate_id=?
    AND session_id=?
    """,
    (
        candidate_id,
        session_id
    ))

    total_events = cursor.fetchone()[0]

    # ------------------------------------
    # Session Duration
    # ------------------------------------

    cursor.execute("""
    SELECT
        start_time,
        end_time

    FROM Session

    WHERE session_id=?
    """,
    (
        session_id,
    ))

    session_data = cursor.fetchone()

    start_time = datetime.strptime(
        session_data[0],
        "%Y-%m-%d %H:%M:%S"
    )

    end_time = datetime.strptime(
        session_data[1],
        "%Y-%m-%d %H:%M:%S"
    )

    duration = end_time - start_time

    total_seconds = int(duration.total_seconds())

    hours = total_seconds // 3600

    minutes = (total_seconds % 3600) // 60

    seconds = total_seconds % 60

    session_duration = (
        f"{hours:02}:{minutes:02}:{seconds:02}"
    )

    # ------------------------------------
    # Event Summary
    # ------------------------------------

    cursor.execute("""
    SELECT
        event_type,
        timestamp

    FROM EventLog

    WHERE
        candidate_id=?
        AND session_id=?

    ORDER BY timestamp ASC
    """,
    (
        candidate_id,
        session_id
    ))

    events = cursor.fetchall()
    event_summary = []

    for event in events:

        event_type = event[0]

        timestamp = event[1]

        deduction = PENALTIES.get(event_type, 0)

        event_summary.append({

            "event_type": event_type,

            "timestamp": timestamp,

            "deduction": deduction

        })


    connection.close()
    

    if camera_manager is not None:

        camera_manager.stop_camera()

        camera_manager = None

    

    return render_template(
        "result.html",

        candidate_id=candidate_id,
        candidate_name=candidate_name,
        session_id=session_id,

        score=result["score"],
        risk=result["risk"],

        face_absence_count=face_absence_count,
        browser_loss_count=browser_loss_count,
        total_events=total_events,
        face_presence_ratio=result["face_presence_ratio"],

        session_duration=session_duration,
        event_summary=event_summary

    )

# ==========================================
# Get Monitoring Status
# ==========================================

@exam.route("/get_monitoring_status")
def get_monitoring_status():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # ----------------------------------
    # Monitoring Status
    # ----------------------------------

    cursor.execute("""

        SELECT
            face_status,
            face_absence_count

        FROM MonitoringStatus

        WHERE candidate_id=?

    """,

    (

        session["candidate_id"],

    ))

    monitoring = cursor.fetchone()

    # ----------------------------------
    # Current Session
    # ----------------------------------

    cursor.execute("""

        SELECT
            start_time,
            end_time,
            status,
            paused_at,
            total_pause_seconds

        FROM Session

        WHERE candidate_id=?

        ORDER BY session_id DESC

        LIMIT 1

    """,

    (

        session["candidate_id"],

    ))

    exam = cursor.fetchone()

    # ----------------------------------
    # Face Status
    # ----------------------------------

    if monitoring:

        face_status = monitoring[0]
        face_absence_count = monitoring[1]

    else:

        face_status = "Unknown"
        face_absence_count = 0

    # ----------------------------------
    # Timer Calculation
    # ----------------------------------

    session_status = "Not Started"
    elapsed_seconds = 0

    if exam:

        start_time = datetime.strptime(

            exam[0],

            "%Y-%m-%d %H:%M:%S"

        )

        end_time = exam[1]

        session_status = exam[2]

        paused_at = exam[3]

        total_pause_seconds = exam[4] or 0

        # --------------------------
        # Running
        # --------------------------

        if session_status == "Running":

            elapsed_seconds = int(

                (datetime.now() - start_time).total_seconds()

            ) - total_pause_seconds

        # --------------------------
        # Paused
        # --------------------------

        elif session_status == "Paused":

            pause_time = datetime.strptime(

                paused_at,

                "%Y-%m-%d %H:%M:%S"

            )

            elapsed_seconds = int(

                (pause_time - start_time).total_seconds()

            ) - total_pause_seconds

        # --------------------------
        # Ended
        # --------------------------

        elif session_status == "Ended":

            if end_time:

                end_time = datetime.strptime(

                    end_time,

                    "%Y-%m-%d %H:%M:%S"

                )

                elapsed_seconds = int(

                    (end_time - start_time).total_seconds()

                ) - total_pause_seconds

    # ----------------------------------
    # Current Integrity Score
    # ----------------------------------

    cursor.execute("""

        SELECT current_score

        FROM IntegrityScore

        WHERE candidate_id=?

        ORDER BY session_id DESC

        LIMIT 1

    """,

    (

        session["candidate_id"],

    ))

    score = cursor.fetchone()

    if score:

        current_score = score[0]

    else:

        current_score = 100

    connection.close()

    return jsonify({

        "face_status": face_status,

        "face_absence_count": face_absence_count,

        "session_status": session_status,

        "elapsed_seconds": max(elapsed_seconds, 0),

        "current_score": current_score

    })

@exam.route("/scores")
def view_scores():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""

        SELECT *

        FROM IntegrityScore

        ORDER BY calculated_at DESC

    """)

    scores = cursor.fetchall()

    connection.close()

    return render_template(
        "scores.html",
        scores=scores
    )    

@exam.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        if (
            username == ADMIN_USERNAME
            and
            password == ADMIN_PASSWORD
        ):

            session["is_admin"] = True

            return redirect(
                url_for("exam.admin_dashboard")
            )

        flash("Invalid Admin Credentials")

    return render_template(
        "admin_login.html"
    )

@exam.route("/admin_dashboard")
def admin_dashboard():

    # --------------------------------
    # Admin Access Protection
    # --------------------------------

    if not session.get("is_admin"):
        return redirect(
            url_for("exam.admin_login")
        )

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # ==========================================================
    # BASIC DASHBOARD STATISTICS
    # ==========================================================

    # -------------------------------
    # Total Candidates
    # -------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM Candidate
    """)

    total_candidates = cursor.fetchone()[0]

    # -------------------------------
    # Active Sessions
    # -------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM Session
        WHERE status='Running'
    """)

    active_sessions = cursor.fetchone()[0]

    # -------------------------------
    # Completed Sessions
    # -------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM Session
        WHERE status='Ended'
    """)

    completed_sessions = cursor.fetchone()[0]

    # -------------------------------
    # Average Integrity Score
    # -------------------------------

    cursor.execute("""
        SELECT ROUND(AVG(final_score), 2)
        FROM IntegrityScore
        WHERE final_score IS NOT NULL
    """)

    result = cursor.fetchone()

    average_score = result[0] if result[0] else 0

    # ==========================================================
    # LATEST INTEGRITY RESULT FOR EACH CANDIDATE
    # ==========================================================

    cursor.execute("""
        SELECT
            c.candidate_id,
            c.name,
            c.email,
            i.final_score,
            i.risk_level,
            i.session_id
        FROM Candidate c
        JOIN IntegrityScore i
            ON c.candidate_id = i.candidate_id
        WHERE i.session_id = (
            SELECT MAX(i2.session_id)
            FROM IntegrityScore i2
            WHERE i2.candidate_id = c.candidate_id
        )
        ORDER BY c.candidate_id
    """)

    candidate_risk_data = cursor.fetchall()

    # ==========================================================
    # RISK DISTRIBUTION DATA
    # Based on latest session of each candidate
    # ==========================================================

    risk_labels = [
        "Excellent",
        "Low Risk",
        "Medium Risk",
        "High Risk",
        "Very High Risk"
    ]

    risk_counts = []

    for risk in risk_labels:

        count = sum(
            1
            for candidate in candidate_risk_data
            if candidate[4] == risk
        )

        risk_counts.append(count)

    # ==========================================================
    # TOTAL SUSPICIOUS EVENTS
    # ==========================================================

    cursor.execute("""
        SELECT COUNT(*)
        FROM EventLog
        WHERE event_type != 'Exam Started'
          AND event_type != 'Exam Ended'
    """)

    total_events = cursor.fetchone()[0]

    # ==========================================================
    # EVENT LOG FILTERS
    # ==========================================================

    candidate_filter = request.args.get(
        "candidate_id", ""
    )

    event_filter = request.args.get(
        "event_type", ""
    )

    date_filter = request.args.get(
        "event_date", ""
    )

    # ==========================================================
    # FETCH EVENT LOGS
    # ==========================================================

    query = """
        SELECT
            rowid AS event_id,
            candidate_id,
            event_type,
            timestamp,
            remarks,
            screenshot_path
        FROM EventLog
        WHERE 1=1
    """

    params = []

    if candidate_filter:
        query += " AND candidate_id=?"
        params.append(candidate_filter)

    if event_filter:
        query += " AND event_type=?"
        params.append(event_filter)

    if date_filter:
        query += " AND DATE(timestamp)=?"
        params.append(date_filter)

    query += " ORDER BY timestamp DESC"

    cursor.execute(query, params)
    

    event_logs = cursor.fetchall()

    # ==========================================================
    # INTEGRITY ANALYTICS
    # ==========================================================

    # -------------------------------
    # Face Absence Events
    # -------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM EventLog
        WHERE event_type='Face Not Detected'
    """)

    total_face_absence = cursor.fetchone()[0]

    # -------------------------------
    # Browser Focus Loss Events
    # -------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM EventLog
        WHERE event_type='Browser Focus Lost'
    """)

    total_browser_loss = cursor.fetchone()[0]

    # -------------------------------
    # Highest Score
    # -------------------------------

    cursor.execute("""
        SELECT MAX(final_score)
        FROM IntegrityScore
        WHERE final_score IS NOT NULL
    """)

    highest_score = cursor.fetchone()[0] or 0

    # -------------------------------
    # Lowest Score
    # -------------------------------

    cursor.execute("""
        SELECT MIN(final_score)
        FROM IntegrityScore
        WHERE final_score IS NOT NULL
    """)

    lowest_score = cursor.fetchone()[0] or 0



    print("\n================ RISK CANDIDATE DATA ================")
    print(candidate_risk_data)
    print("======================================================\n")

    # ==========================================================
    # CLOSE DATABASE
    # ==========================================================

    connection.close()

    # ==========================================================
    # SEND DATA TO ADMIN DASHBOARD
    # ==========================================================

    return render_template(
        "admin_dashboard.html",

        total_candidates=total_candidates,

        active_sessions=active_sessions,

        completed_sessions=completed_sessions,

        average_score=average_score,

        total_events=total_events,

        event_logs=event_logs,
        

        # Candidate risk information
        candidate_risk_data=candidate_risk_data,

        # risk chart information
    
        risk_labels=risk_labels,
        risk_counts=risk_counts,

        # Filters
        candidate_filter=candidate_filter,
        event_filter=event_filter,
        date_filter=date_filter,

        # Integrity analytics
        total_face_absence=total_face_absence,

        total_browser_loss=total_browser_loss,

        highest_score=highest_score,

        lowest_score=lowest_score
    )


@exam.route("/admin_logout")
def admin_logout():

    session.pop("is_admin", None)

    return redirect(
        url_for("home")
    )

# ==========================================
# View Evidence
# ==========================================

@exam.route("/evidence/<path:filename>")
def view_evidence(filename):

    evidence_folder = os.path.join(os.getcwd(), "evidence")

    return send_from_directory(
        evidence_folder,
        filename
    )    

@exam.route("/evidence-details/<int:event_id>")
def evidence_details(event_id):

    # -----------------------------------------
    # Admin authentication
    # -----------------------------------------

    if not session.get("is_admin"):
        return redirect(
            url_for("exam.admin_login")
        )

    # -----------------------------------------
    # Connect to database
    # -----------------------------------------

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # -----------------------------------------
    # Get event information
    # -----------------------------------------

    cursor.execute("""
        SELECT
            rowid,
            candidate_id,
            event_type,
            timestamp,
            remarks,
            screenshot_path
        FROM EventLog
        WHERE rowid=?
    """, (event_id,))

    event = cursor.fetchone()

    connection.close()

    # -----------------------------------------
    # Event not found
    # -----------------------------------------

    if not event:
        return "Event not found", 404

    # -----------------------------------------
    # Send event information to template
    # -----------------------------------------

    return render_template(
        "evidence_viewer.html",
        event=event
    )    

# ==========================================================
# Download Current Event Logs
# ==========================================================

@exam.route("/download_event_logs")
def download_event_logs():

    if not session.get("is_admin"):
        return redirect(url_for("exam.admin_login"))

    candidate_filter = request.args.get("candidate_id", "")
    event_filter = request.args.get("event_type", "")
    date_filter = request.args.get("event_date", "")

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    query = """
        SELECT
            rowid AS event_id,
            candidate_id,
            event_type,
            timestamp,
            remarks,
            screenshot_path
        FROM EventLog
        WHERE 1=1
    """

    params = []

    # Candidate filter
    if candidate_filter:

        query += " AND candidate_id=?"
        params.append(candidate_filter)

    # Event type filter
    if event_filter:

        query += " AND event_type=?"
        params.append(event_filter)

    # Date filter
    if date_filter:

        query += " AND DATE(timestamp)=?"
        params.append(date_filter)

    query += " ORDER BY timestamp DESC"

    cursor.execute(query, params)

    events = cursor.fetchall()

    connection.close()

    # ------------------------------------------------------
    # Create CSV in memory
    # ------------------------------------------------------

    output = io.StringIO()

    writer = csv.writer(output)

    # CSV Header
    writer.writerow([
        "Event ID",
        "Candidate ID",
        "Event Type",
        "Timestamp",
        "Remarks",
        "Screenshot Path"
    ])

    # CSV Data
    for event in events:

        writer.writerow(event)

    # ------------------------------------------------------
    # Send CSV file to browser
    # ------------------------------------------------------

    response = Response(
        output.getvalue(),
        mimetype="text/csv"
    )

    response.headers["Content-Disposition"] = (
        "attachment; filename=event_logs.csv"
    )

    return response
    
# ==========================================================
# Download Selected Event Logs
# ==========================================================

@exam.route("/download_selected_events", methods=["POST"])
def download_selected_events():

    if not session.get("is_admin"):
        return redirect(url_for("exam.admin_login"))

    selected_events = request.form.getlist("selected_events")

    # ------------------------------------------------------
    # Nothing selected
    # ------------------------------------------------------

    if not selected_events:

        return redirect(
            url_for("exam.admin_dashboard")
        )

    # Convert IDs to integers
    try:

        selected_ids = [
            int(event_id)
            for event_id in selected_events
        ]

    except ValueError:

        return redirect(
            url_for("exam.admin_dashboard")
        )

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    # ------------------------------------------------------
    # Create placeholders
    # ------------------------------------------------------

    placeholders = ",".join(
        ["?"] * len(selected_ids)
    )

    query = f"""
        SELECT
            rowid AS event_id,
            candidate_id,
            event_type,
            timestamp,
            remarks,
            screenshot_path
        FROM EventLog
        WHERE rowid IN ({placeholders})
        ORDER BY timestamp DESC
    """

    cursor.execute(
        query,
        selected_ids
    )

    events = cursor.fetchall()

    connection.close()

    # ------------------------------------------------------
    # Create CSV
    # ------------------------------------------------------

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Event ID",
        "Candidate ID",
        "Event Type",
        "Timestamp",
        "Remarks",
        "Screenshot Path"
    ])

    for event in events:

        writer.writerow(event)

    # ------------------------------------------------------
    # Send CSV
    # ------------------------------------------------------

    response = Response(
        output.getvalue(),
        mimetype="text/csv"
    )

    response.headers["Content-Disposition"] = (
        "attachment; filename=selected_event_logs.csv"
    )

    return response