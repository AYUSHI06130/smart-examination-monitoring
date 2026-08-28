# Testing Documentation

## Project Title

Development of Smart Examination Monitoring Platform with Integrity Analysis & Reporting System

---

## 1. Testing Objective

The objective of testing is to verify that the Smart Examination Monitoring Platform performs the required examination monitoring, event logging, evidence capture, integrity analysis, and reporting functions correctly.

---

## 2. Functional Testing

| Test ID | Test Case | Expected Result | Status |
|---|---|---|---|
| T01 | Open application | Application opens successfully | Pass |
| T02 | Access examination | Examination page loads correctly | Pass |
| T03 | Camera access | Camera starts successfully | Pass |
| T04 | Face detection | Candidate face is detected | Pass |
| T05 | Face absence | Suspicious event is generated | Pass |
| T06 | Multiple faces | Multiple-face event is generated | Pass |
| T07 | Browser focus loss | Focus-loss event is recorded | Pass |
| T08 | Tab switching | Tab-switch event is recorded | Pass |
| T09 | Suspicious event | Event is stored in database | Pass |
| T10 | Screenshot capture | Screenshot is saved | Pass |
| T11 | Screenshot path | Correct path is stored | Pass |
| T12 | Multiple screenshots | Previous screenshots are not overwritten | Pass |
| T13 | Integrity analysis | Integrity score is generated | Pass |
| T14 | Admin dashboard | Session information is displayed | Pass |
| T15 | Examination report | Report displays required information | Pass |

---

## 3. Face Monitoring Test

### Test

Test the system when a candidate's face is visible and when the face is absent.

### Expected Result

The system should identify the candidate's face and detect the required face absence condition.

### Result

Pass.

---

## 4. Multiple Face Test

### Test

Place more than one face within the camera view.

### Expected Result

The system should identify the multiple-face condition and record the appropriate event.

### Result

Pass.

---

## 5. Browser Focus Test

### Test

Move the browser focus away from the examination page.

### Expected Result

A browser focus-loss event should be recorded.

### Result

Pass.

---

## 6. Tab Switching Test

### Test

Switch from the examination tab to another browser tab.

### Expected Result

A tab-switch event should be recorded.

### Result

Pass.

---

## 7. Screenshot Testing

### Test

Trigger a suspicious event that requires evidence capture.

### Expected Result

A screenshot should be captured and saved inside the candidate's evidence folder.
