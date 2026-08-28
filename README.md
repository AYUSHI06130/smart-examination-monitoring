# Development of Smart Examination Monitoring Platform with Integrity Analysis & Reporting System

##  Project Overview

The **Smart Examination Monitoring Platform with Integrity Analysis & Reporting System** is an online examination monitoring solution designed to improve the reliability and integrity of online examinations.

The system monitors candidate activities during an examination and identifies potentially suspicious activities such as face absence, multiple faces, browser focus loss, and tab switching.

Suspicious activities are recorded as events, and relevant evidence screenshots can be captured and stored. The collected information is used to calculate an integrity score and generate an examination session report for administrators.

---

##  Project Objectives

The main objectives of this project are:

- To monitor candidates during online examinations.
- To detect the presence or absence of a candidate's face.
- To detect multiple faces appearing during an examination.
- To monitor browser focus.
- To detect tab switching during an examination.
- To record suspicious examination events.
- To automatically capture screenshots as evidence for suspicious events.
- To store event and screenshot information in the database.
- To calculate an examination integrity score.
- To provide an admin dashboard for monitoring examination sessions.
- To generate an integrity analysis and examination report.

---

##  Key Features

### Candidate Monitoring

- Face detection using OpenCV.
- Face absence monitoring.
- Multiple-face detection.
- Candidate examination session monitoring.

### Browser Monitoring

- Browser focus-loss detection.
- Tab-switch detection.
- Suspicious browser activity logging.

### Evidence Management

- Automatic screenshot capture for selected suspicious events.
- Candidate-specific evidence folders.
- Timestamp-based screenshot filenames.
- Screenshot path storage in the database.
- Multiple evidence screenshots without overwriting previous files.

### Integrity Analysis

- Suspicious event counting.
- Integrity score calculation.
- Session-level integrity analysis.

### Reporting

- Candidate information.
- Examination session information.
- Integrity score.
- Suspicious event summary.
- Evidence/screenshot references.
- Admin examination report.

### Administration

- Admin dashboard.
- Examination session monitoring.
- Event log viewing.
- Integrity report viewing.

---

##  Technology Stack

### Frontend

- HTML5
- CSS3
- JavaScript

### Backend

- Python
- Flask

### Database

- SQLite

### Computer Vision

- OpenCV

### Version Control

- Git
- GitHub

---

##  Project Structure

```text
.
├── database/
│ └── Database-related files
│
├── evidence/
│ └── Candidate_123456/
│ └── Evidence screenshots
│
├── models/
│ └── Application data models
│
├── routes/
│ └── Flask application routes
│
├── static/
│ ├── css/
│ ├── js/
│ └── images/
│
├── templates/
│ └── HTML templates
│
├── utils/
│ └── Utility and monitoring functions
│
├── agile-documentation/
│ ├── project-plan.md
│ ├── product-backlog.md
│ ├── sprint-1.md
│ ├── sprint-2.md
│ ├── sprint-3.md
│ ├── testing.md
│ └── daily-progress.md
│
├── app.py
├── config.py
├── check_db.py
├── test_camera.py
├── testpage.html
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
