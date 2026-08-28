# Sprint 3 – Evidence, Integrity Analysis and Reporting

## Project Title

Development of Smart Examination Monitoring Platform with Integrity Analysis & Reporting System

---

## Sprint Goal

To implement evidence management, integrity analysis, examination reporting, and final testing.

---

## Planned Tasks

- Implement automatic screenshot capture.
- Create candidate-specific evidence folders.
- Generate unique screenshot filenames.
- Store screenshot paths in the database.
- Associate screenshots with suspicious events.
- Implement integrity score calculation.
- Generate examination session reports.
- Perform final system testing.

---

## Task Status

| Task | Status |
|---|---|
| Screenshot capture | Completed |
| Evidence folder organization | Completed |
| Unique screenshot filenames | Completed |
| Screenshot path storage | Completed |
| Event-evidence association | Completed |
| Integrity score calculation | Completed |
| Examination report | Completed |
| Final testing | Completed |

---

## Evidence Structure

```text
evidence/
└── Candidate_123456/
    ├── browser_focus_lost_23-17-20.png
    ├── browser_focus_lost_23-17-23.png
    ├── face_missing_23-17-16.png
    └── face_missing_23-17-26.png
