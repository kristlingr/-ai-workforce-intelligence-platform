# Data Dictionary - AI Workforce Intelligence Agent

This document defines the schema, data types, constraints, and business rules for all cleaned CSV datasets in the data layer.

---

## 1. Employees Dataset (`employees.csv`)
**Purpose:** Stores anonymized profile information for all company employees.

| Column Name | Data Type | Nullable? | Primary/Foreign Key | Description / Allowed Values | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `employee_id` | String | No | Primary Key | Unique employee identifier (e.g., EMP001) | `EMP001` |
| `department` | String | No | - | Department name: Engineering, Product, Design, HR, Sales | `Engineering` |
| `role` | String | No | - | Specific job role (e.g., Senior Software Engineer, Product Manager) | `Software Engineer` |
| `hire_date` | String | No | - | Employee hire date (YYYY-MM-DD) | `2023-04-08` |
| `status` | String | No | - | Current employment status: Active, On Leave, Terminated | `Active` |
| `work_type` | String | No | - | Physical work model: Remote, Hybrid, On-site | `Remote` |
| `location` | String | No | - | Base office location (e.g., San Francisco, Berlin, Remote) | `Remote` |
| `salary_band` | String | No | - | Anonymized salary level: Band 1 to Band 4 | `Band 2` |

---

## 2. Worklogs Dataset (`worklogs.csv`)
**Purpose:** Logs daily hours spent by employees on different projects and activities.

| Column Name | Data Type | Nullable? | Primary/Foreign Key | Description / Allowed Values | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `worklog_id` | String | No | Primary Key | Unique worklog identifier (e.g., WL00001) | `WL00001` |
| `employee_id` | String | No | Foreign Key -> `Employees` | Unique employee identifier (e.g., EMP001) | `EMP001` |
| `date` | String | No | - | Date on which work or attendance was tracked (YYYY-MM-DD) | `2026-05-27` |
| `project_id` | String | No | - | Project identifier (e.g., PRJ001 or PRJ_INTERNAL) | `PRJ004` |
| `hours_logged` | Float | No | - | Number of hours spent on the task (0.1 to 24.0) | `6.2` |
| `task_category` | String | No | - | Activity category: Development, Design, Meetings, Admin, Research, Support | `Development` |
| `description` | String | No | - | Brief, anonymized details about the tasks accomplished | `Writing unit tests and bug fixes` |

---

## 3. Project Allocation Dataset (`project_allocations.csv`)
**Purpose:** Defines planned capacity allocation percentages for employees on active projects.

| Column Name | Data Type | Nullable? | Primary/Foreign Key | Description / Allowed Values | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `allocation_id` | String | No | Primary Key | Unique allocation identifier (e.g., AL001) | `AL001` |
| `project_id` | String | No | - | Project identifier (e.g., PRJ001 or PRJ_INTERNAL) | `PRJ004` |
| `project_name` | String | No | - | Human-readable project name (e.g., Cloud Migration) | `Sales Pipeline Automation` |
| `employee_id` | String | No | Foreign Key -> `Employees` | Unique employee identifier (e.g., EMP001) | `EMP001` |
| `allocation_percentage` | Float | No | - | Proportion of working hours dedicated (0.0 to 1.0) | `0.7` |
| `start_date` | String | No | - | Start date of the allocation period (YYYY-MM-DD) | `2026-01-01` |
| `end_date` | String | No | - | End date of the allocation period (YYYY-MM-DD) | `2026-12-31` |
| `role_on_project` | String | No | - | Project role: Lead or Contributor | `Contributor` |
| `project_category` | String | No | - | Automatically classified project category (e.g., Infrastructure, Development) | `Development` |

---

## 4. Attendance Dataset (`attendance.csv`)
**Purpose:** Details daily attendance, absences, leaves, and core check-in/out timestamps.

| Column Name | Data Type | Nullable? | Primary/Foreign Key | Description / Allowed Values | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `attendance_id` | String | No | Primary Key | Unique attendance identifier (e.g., ATT00001) | `ATT00001` |
| `employee_id` | String | No | Foreign Key -> `Employees` | Unique employee identifier (e.g., EMP001) | `EMP001` |
| `date` | String | No | - | Date on which work or attendance was tracked (YYYY-MM-DD) | `2026-05-27` |
| `status` | String | No | - | Current employment status: Active, On Leave, Terminated | `Present` |
| `check_in_time` | String | No | - | Core check-in timestamp (HH:MM) - only present if status is Present | `09:04` |
| `check_out_time` | String | No | - | Core check-out timestamp (HH:MM) - only present if status is Present | `17:35` |

---

## 5. Capacity Dataset (`capacity.csv`)
**Purpose:** Holds monthly capacity limits and standard working hours per employee.

| Column Name | Data Type | Nullable? | Primary/Foreign Key | Description / Allowed Values | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `capacity_id` | String | No | Primary Key | Unique capacity identifier (e.g., CAP001) | `CAP001` |
| `employee_id` | String | No | Foreign Key -> `Employees` | Unique employee identifier (e.g., EMP001) | `EMP001` |
| `month` | String | No | - | Month of capacity details (YYYY-MM) | `2026-05` |
| `working_days` | Integer | No | - | Total number of weekdays (excluding weekends) in the month | `21` |
| `standard_hours_per_day` | Float | No | - | Number of standard hours per workday (defaults to 8.0) | `8.0` |
| `total_capacity_hours` | Float | No | - | Maximum total capacity in hours (working_days * standard_hours_per_day) | `168.0` |
| `available_hours` | Float | No | - | Available working capacity in hours (total capacity minus PTO/leave hours) | `160.0` |

---

## 6. Business Validation Rules Enforced
The validation suite enforces structural schemas, primary key constraints, foreign key referential integrity, and logical business boundaries (e.g. valid logs within capacity, check-in bounds, overallocation constraints).