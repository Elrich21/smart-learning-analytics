# Data Model Specification

This document describes the core data entities and their relationships used in the Smart Learning Analytics Platform.

---

## 1. User

Represents a student using the platform.

**Attributes:**
- user_id (Primary Key)
- name
- email (unique)
- password_hash
- degree
- academic_year
- created_at

**Description:**
Stores authentication and profile-related information for each user.

---

## 2. Course

Represents an academic subject or course.

**Attributes:**
- course_id (Primary Key)
- course_name
- difficulty_level

**Description:**
Used to categorize study sessions and performance data by subject.

---

## 3. StudySession

Represents a single study activity logged by a user.

**Attributes:**
- session_id (Primary Key)
- user_id (Foreign Key → User)
- course_id (Foreign Key → Course)
- duration_minutes
- study_method (e.g., reading, video, practice)
- focus_score (1–5)
- time_of_day (morning, afternoon, night)
- session_date

**Description:**
Captures behavioral learning data that forms the basis for analytics and machine learning predictions.

---

## 4. Performance

Represents academic performance metrics for a user in a specific course.

**Attributes:**
- performance_id (Primary Key)
- user_id (Foreign Key → User)
- course_id (Foreign Key → Course)
- previous_score
- predicted_score
- risk_level (Low / Medium / High)

**Description:**
Stores both historical and predicted academic performance data.

---

## 5. Relationships

- A User can have multiple StudySessions
- A Course can have multiple StudySessions
- A User–Course pair has one Performance record

These relationships enable efficient analysis of learning behavior and performance trends.
