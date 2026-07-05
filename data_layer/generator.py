"""
Data Generator Module for AI Workforce Intelligence Agent.
Generates realistic, anonymized, and internally consistent CSV datasets for employees,
project allocations, attendance, worklogs, and capacity limits.
"""

import os
import random
import datetime
import pandas as pd
import numpy as np
from data_layer import (
    DATASETS_DIR,
    EMPLOYEES_FILE,
    WORKLOGS_FILE,
    ALLOCATIONS_FILE,
    ATTENDANCE_FILE,
    CAPACITY_FILE,
    get_dataset_path
)

def generate_datasets(seed: int = 42):
    """Generates all workforce datasets with realistic, consistent data."""
    # Ensure reproducibility
    random.seed(seed)
    np.random.seed(seed)
    
    # Ensure directory exists
    os.makedirs(DATASETS_DIR, exist_ok=True)
    
    print("Generating datasets...")
    
    # ----------------------------------------------------
    # 1. Employees Dataset
    # ----------------------------------------------------
    departments_roles = {
        "Engineering": [
            ("Software Engineer", "Band 2"),
            ("Senior Software Engineer", "Band 3"),
            ("QA Engineer", "Band 2"),
            ("DevOps Engineer", "Band 2"),
            ("Engineering Manager", "Band 4")
        ],
        "Product": [
            ("Product Manager", "Band 3"),
            ("Senior Product Manager", "Band 4")
        ],
        "Design": [
            ("UX Designer", "Band 2"),
            ("Visual Designer", "Band 1")
        ],
        "HR": [
            ("HR Specialist", "Band 1"),
            ("HR Manager", "Band 3")
        ],
        "Sales": [
            ("Sales Representative", "Band 1"),
            ("Sales Manager", "Band 3")
        ]
    }
    
    locations = ["New York", "San Francisco", "London", "Berlin", "Remote"]
    work_types = ["Remote", "Hybrid", "On-site"]
    
    employees = []
    # 15 Employees
    for i in range(1, 16):
        emp_id = f"EMP{i:03d}"
        
        # Pick department
        dept = random.choice(list(departments_roles.keys()))
        role, band = random.choice(departments_roles[dept])
        
        # Hire date in the last few years
        start_year = random.randint(2021, 2025)
        start_month = random.randint(1, 12)
        start_day = random.randint(1, 28)
        hire_date = datetime.date(start_year, start_month, start_day)
        
        # Status distribution: 13 Active, 1 On Leave, 1 Terminated
        if i == 14:
            status = "On Leave"
        elif i == 15:
            status = "Terminated"
        else:
            status = "Active"
            
        work_type = random.choice(work_types)
        loc = "Remote" if work_type == "Remote" else random.choice(locations[:-1])
        
        employees.append({
            "employee_id": emp_id,
            "department": dept,
            "role": role,
            "hire_date": hire_date.isoformat(),
            "status": status,
            "work_type": work_type,
            "location": loc,
            "salary_band": band
        })
        
    df_employees = pd.DataFrame(employees)
    employees_path = get_dataset_path(EMPLOYEES_FILE)
    df_employees.to_csv(employees_path, index=False)
    print(f"Saved: {employees_path} ({len(df_employees)} rows)")

    # ----------------------------------------------------
    # 2. Projects & Allocations Dataset
    # ----------------------------------------------------
    projects = [
        {"project_id": "PRJ001", "project_name": "Cloud Migration", "dept": "Engineering"},
        {"project_id": "PRJ002", "project_name": "Mobile App V2", "dept": "Product/Engineering/Design"},
        {"project_id": "PRJ003", "project_name": "HR Portal Integration", "dept": "HR/Engineering"},
        {"project_id": "PRJ004", "project_name": "Sales Pipeline Automation", "dept": "Sales/Product/Engineering"},
        {"project_id": "PRJ005", "project_name": "Security Audit", "dept": "Engineering"},
        {"project_id": "PRJ_INTERNAL", "project_name": "Internal Operations", "dept": "All"}
    ]
    
    allocations = []
    alloc_id_counter = 1
    
    # Define start and end date for current allocations
    alloc_start = datetime.date(2026, 1, 1)
    alloc_end = datetime.date(2026, 12, 31)
    
    for emp in employees:
        emp_id = emp["employee_id"]
        status = emp["status"]
        dept = emp["department"]
        role = emp["role"]
        
        # Terminated employees have no active allocations
        if status == "Terminated":
            continue
            
        # Determine allocations based on role/department
        if status == "On Leave":
            # Still allocated but currently inactive (can have 100% allocation to internal or primary)
            allocations.append({
                "allocation_id": f"AL{alloc_id_counter:03d}",
                "project_id": "PRJ_INTERNAL",
                "project_name": "Internal Operations",
                "employee_id": emp_id,
                "allocation_percentage": 1.0,
                "start_date": alloc_start.isoformat(),
                "end_date": alloc_end.isoformat(),
                "role_on_project": "Contributor"
            })
            alloc_id_counter += 1
            continue
            
        # For active employees:
        if dept == "HR":
            # HR primarily works on HR Integration and Internal Operations
            allocations.append({
                "allocation_id": f"AL{alloc_id_counter:03d}",
                "project_id": "PRJ003",
                "project_name": "HR Portal Integration",
                "employee_id": emp_id,
                "allocation_percentage": 0.6,
                "start_date": alloc_start.isoformat(),
                "end_date": alloc_end.isoformat(),
                "role_on_project": "Lead" if "Manager" in role else "Contributor"
            })
            alloc_id_counter += 1
            allocations.append({
                "allocation_id": f"AL{alloc_id_counter:03d}",
                "project_id": "PRJ_INTERNAL",
                "project_name": "Internal Operations",
                "employee_id": emp_id,
                "allocation_percentage": 0.4,
                "start_date": alloc_start.isoformat(),
                "end_date": alloc_end.isoformat(),
                "role_on_project": "Contributor"
            })
            alloc_id_counter += 1
            
        elif dept == "Sales":
            # Sales works on Sales Automation and Internal Operations
            allocations.append({
                "allocation_id": f"AL{alloc_id_counter:03d}",
                "project_id": "PRJ004",
                "project_name": "Sales Pipeline Automation",
                "employee_id": emp_id,
                "allocation_percentage": 0.8,
                "start_date": alloc_start.isoformat(),
                "end_date": alloc_end.isoformat(),
                "role_on_project": "Lead" if "Manager" in role else "Contributor"
            })
            alloc_id_counter += 1
            allocations.append({
                "allocation_id": f"AL{alloc_id_counter:03d}",
                "project_id": "PRJ_INTERNAL",
                "project_name": "Internal Operations",
                "employee_id": emp_id,
                "allocation_percentage": 0.2,
                "start_date": alloc_start.isoformat(),
                "end_date": alloc_end.isoformat(),
                "role_on_project": "Contributor"
            })
            alloc_id_counter += 1
            
        elif dept == "Design":
            # Design split between Mobile App and Internal
            allocations.append({
                "allocation_id": f"AL{alloc_id_counter:03d}",
                "project_id": "PRJ002",
                "project_name": "Mobile App V2",
                "employee_id": emp_id,
                "allocation_percentage": 0.7,
                "start_date": alloc_start.isoformat(),
                "end_date": alloc_end.isoformat(),
                "role_on_project": "Contributor"
            })
            alloc_id_counter += 1
            allocations.append({
                "allocation_id": f"AL{alloc_id_counter:03d}",
                "project_id": "PRJ_INTERNAL",
                "project_name": "Internal Operations",
                "employee_id": emp_id,
                "allocation_percentage": 0.3,
                "start_date": alloc_start.isoformat(),
                "end_date": alloc_end.isoformat(),
                "role_on_project": "Contributor"
            })
            alloc_id_counter += 1
            
        elif dept == "Product":
            # Product split between Mobile App and Sales Automation
            allocations.append({
                "allocation_id": f"AL{alloc_id_counter:03d}",
                "project_id": "PRJ002",
                "project_name": "Mobile App V2",
                "employee_id": emp_id,
                "allocation_percentage": 0.5,
                "start_date": alloc_start.isoformat(),
                "end_date": alloc_end.isoformat(),
                "role_on_project": "Lead" if "Senior" in role else "Contributor"
            })
            alloc_id_counter += 1
            allocations.append({
                "allocation_id": f"AL{alloc_id_counter:03d}",
                "project_id": "PRJ004",
                "project_name": "Sales Pipeline Automation",
                "employee_id": emp_id,
                "allocation_percentage": 0.5,
                "start_date": alloc_start.isoformat(),
                "end_date": alloc_end.isoformat(),
                "role_on_project": "Lead" if "Senior" in role else "Contributor"
            })
            alloc_id_counter += 1
            
        elif dept == "Engineering":
            # Engineers can be allocated to Cloud Migration, Mobile App, HR Integration, Security Audit
            # Choose 2 projects randomly
            eng_projects = [
                ("PRJ001", "Cloud Migration"),
                ("PRJ002", "Mobile App V2"),
                ("PRJ003", "HR Portal Integration"),
                ("PRJ004", "Sales Pipeline Automation"),
                ("PRJ005", "Security Audit")
            ]
            chosen = random.sample(eng_projects, 2)
            
            # Allocation split (e.g., 0.5 / 0.5, or 0.7 / 0.3, or 0.6 / 0.4)
            alloc_split = random.choice([0.5, 0.6, 0.7])
            
            allocations.append({
                "allocation_id": f"AL{alloc_id_counter:03d}",
                "project_id": chosen[0][0],
                "project_name": chosen[0][1],
                "employee_id": emp_id,
                "allocation_percentage": alloc_split,
                "start_date": alloc_start.isoformat(),
                "end_date": alloc_end.isoformat(),
                "role_on_project": "Lead" if "Manager" in role else "Contributor"
            })
            alloc_id_counter += 1
            
            allocations.append({
                "allocation_id": f"AL{alloc_id_counter:03d}",
                "project_id": chosen[1][0],
                "project_name": chosen[1][1],
                "employee_id": emp_id,
                "allocation_percentage": round(1.0 - alloc_split, 1),
                "start_date": alloc_start.isoformat(),
                "end_date": alloc_end.isoformat(),
                "role_on_project": "Contributor"
            })
            alloc_id_counter += 1

    df_allocations = pd.DataFrame(allocations)
    allocations_path = get_dataset_path(ALLOCATIONS_FILE)
    df_allocations.to_csv(allocations_path, index=False)
    print(f"Saved: {allocations_path} ({len(df_allocations)} rows)")

    # ----------------------------------------------------
    # 3. Attendance & Worklogs (Generated day-by-day)
    # ----------------------------------------------------
    # Generate for the past 30 days up to 2026-06-25
    end_date = datetime.date(2026, 6, 25)
    start_date = end_date - datetime.timedelta(days=29)
    
    # All dates in range
    date_list = [start_date + datetime.timedelta(days=x) for x in range(30)]
    
    attendance = []
    worklogs = []
    
    att_id_counter = 1
    wl_id_counter = 1
    
    # Task descriptions per category for realistic logs
    descriptions = {
        "Development": [
            "Writing unit tests and bug fixes",
            "Refactoring API response serialization",
            "Implementing OAuth2 authorization endpoints",
            "Integrating databases with Redis caching",
            "Optimizing Docker container builds",
            "Debugging SQL slow queries"
        ],
        "Design": [
            "Designing user profile wireframes",
            "Iterating on Figma design system components",
            "Conducting user research interviews",
            "Creating high-fidelity mobile app mockups",
            "Reviewing accessibility contrast and typography"
        ],
        "Meetings": [
            "Daily team standup and sprint alignment",
            "Sprint planning and story pointing",
            "Monthly company sync",
            "Client demo and feedback session",
            "1-on-1 career development meeting"
        ],
        "Admin": [
            "Reviewing compliance documents",
            "Timesheet submission and email cleanup",
            "System configuration updates",
            "Documenting team onboarding guidelines"
        ],
        "Research": [
            "Researching Vector DB options for RAG pipeline",
            "Evaluating frontend state management libraries",
            "Benchmarking LLM model inference speeds",
            "Reviewing security compliance specifications"
        ],
        "Support": [
            "Investigating production server outage logs",
            "Resolving customer escalated ticket on login issue",
            "Helping team member with database migrations",
            "Writing developer integration guide"
        ]
    }
    
    # Generate records
    for dt in date_list:
        is_weekend = dt.weekday() >= 5  # Saturday or Sunday
        
        for emp in employees:
            emp_id = emp["employee_id"]
            status = emp["status"]
            
            # Skip terminated employees entirely
            if status == "Terminated":
                continue
                
            # If On Leave:
            if status == "On Leave":
                # Attendance is "On Leave"
                attendance.append({
                    "attendance_id": f"ATT{att_id_counter:05d}",
                    "employee_id": emp_id,
                    "date": dt.isoformat(),
                    "status": "On Leave",
                    "check_in_time": "",
                    "check_out_time": ""
                })
                att_id_counter += 1
                # No worklogs generated for On Leave
                continue
                
            # For Active employees:
            if is_weekend:
                # Weekend off
                attendance.append({
                    "attendance_id": f"ATT{att_id_counter:05d}",
                    "employee_id": emp_id,
                    "date": dt.isoformat(),
                    "status": "Weekend",
                    "check_in_time": "",
                    "check_out_time": ""
                })
                att_id_counter += 1
                # No worklogs on weekend
                continue
                
            # Weekdays for Active employees:
            # 90% Present, 5% PTO, 3% Sick Leave, 2% Absent
            rand = random.random()
            if rand < 0.90:
                att_status = "Present"
                # Check in between 08:30 and 09:30
                check_in_hour = 8
                check_in_minute = random.randint(30, 59)
                if random.random() > 0.5:
                    check_in_hour = 9
                    check_in_minute = random.randint(0, 30)
                
                # Check out after 7.5 to 9.5 hours
                work_duration = random.uniform(7.5, 9.5)
                check_in_decimal = check_in_hour + check_in_minute / 60.0
                check_out_decimal = check_in_decimal + work_duration
                
                check_out_hour = int(check_out_decimal)
                check_out_minute = int((check_out_decimal - check_out_hour) * 60)
                
                check_in_str = f"{check_in_hour:02d}:{check_in_minute:02d}"
                check_out_str = f"{check_out_hour:02d}:{check_out_minute:02d}"
                
                attendance.append({
                    "attendance_id": f"ATT{att_id_counter:05d}",
                    "employee_id": emp_id,
                    "date": dt.isoformat(),
                    "status": att_status,
                    "check_in_time": check_in_str,
                    "check_out_time": check_out_str
                })
                att_id_counter += 1
                
                # Generate worklogs for this day
                # Get this employee's allocations
                emp_allocs = [a for a in allocations if a["employee_id"] == emp_id]
                
                if len(emp_allocs) == 0:
                    # Fallback (internal operations)
                    emp_allocs = [{
                        "project_id": "PRJ_INTERNAL",
                        "allocation_percentage": 1.0
                    }]
                
                # Distribute the hours worked based on allocation percentage
                remaining_hours = round(work_duration, 1)
                num_allocs = len(emp_allocs)
                
                for idx, alloc in enumerate(emp_allocs):
                    proj_id = alloc["project_id"]
                    alloc_pct = alloc["allocation_percentage"]
                    
                    if idx == num_allocs - 1:
                        # Last project gets remaining hours
                        hours_logged = round(remaining_hours, 1)
                    else:
                        # Log hours based on allocation pct with a bit of noise
                        target_hours = work_duration * alloc_pct
                        hours_logged = round(np.random.normal(target_hours, 0.4), 1)
                        # Clamping
                        hours_logged = max(1.0, min(hours_logged, remaining_hours - 1.0))
                        remaining_hours -= hours_logged
                    
                    # Choose a task category based on department
                    dept = emp["department"]
                    if dept == "Engineering":
                        cat = random.choices(["Development", "Meetings", "Research", "Support"], weights=[0.6, 0.15, 0.15, 0.10])[0]
                    elif dept == "Design":
                        cat = random.choices(["Design", "Meetings", "Research"], weights=[0.7, 0.15, 0.15])[0]
                    elif dept == "Product":
                        cat = random.choices(["Meetings", "Research", "Admin"], weights=[0.5, 0.3, 0.2])[0]
                    elif dept == "HR":
                        cat = random.choices(["Admin", "Meetings", "Support"], weights=[0.6, 0.2, 0.2])[0]
                    else:  # Sales
                        cat = random.choices(["Support", "Meetings", "Admin"], weights=[0.6, 0.2, 0.2])[0]
                        
                    desc = random.choice(descriptions[cat])
                    
                    worklogs.append({
                        "worklog_id": f"WL{wl_id_counter:05d}",
                        "employee_id": emp_id,
                        "date": dt.isoformat(),
                        "project_id": proj_id,
                        "hours_logged": hours_logged,
                        "task_category": cat,
                        "description": desc
                    })
                    wl_id_counter += 1
                
            else:
                # Sick Leave, PTO, or Absent
                att_status = "PTO" if rand < 0.95 else ("Sick Leave" if rand < 0.98 else "Absent")
                attendance.append({
                    "attendance_id": f"ATT{att_id_counter:05d}",
                    "employee_id": emp_id,
                    "date": dt.isoformat(),
                    "status": att_status,
                    "check_in_time": "",
                    "check_out_time": ""
                })
                att_id_counter += 1
                # No worklogs generated

    df_attendance = pd.DataFrame(attendance)
    attendance_path = get_dataset_path(ATTENDANCE_FILE)
    df_attendance.to_csv(attendance_path, index=False)
    print(f"Saved: {attendance_path} ({len(df_attendance)} rows)")
    
    df_worklogs = pd.DataFrame(worklogs)
    worklogs_path = get_dataset_path(WORKLOGS_FILE)
    df_worklogs.to_csv(worklogs_path, index=False)
    print(f"Saved: {worklogs_path} ({len(df_worklogs)} rows)")

    # ----------------------------------------------------
    # 4. Capacity Dataset
    # ----------------------------------------------------
    # Calculated for May and June 2026 based on working days and leaves
    months = ["2026-05", "2026-06"]
    capacity = []
    cap_id_counter = 1
    
    # Calculate weekdays in May and June 2026
    # May 2026: starts Friday May 1, ends Sunday May 31. Total weekdays: 21 (since May 1 is Friday, May 2-3 weekend...)
    # Let's count them programmatically using pandas date_range
    for month in months:
        yr, mn = map(int, month.split("-"))
        # Start and end of month
        m_start = datetime.date(yr, mn, 1)
        if mn == 12:
            m_end = datetime.date(yr + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            m_end = datetime.date(yr, mn + 1, 1) - datetime.timedelta(days=1)
            
        all_month_dates = pd.date_range(m_start, m_end)
        weekdays = [d for d in all_month_dates if d.weekday() < 5]
        num_weekdays = len(weekdays)
        
        # Parse attendance dates in this month to calculate PTO/leaves for each employee
        df_att_month = df_attendance[df_attendance["date"].str.startswith(month)]
        
        for emp in employees:
            emp_id = emp["employee_id"]
            status = emp["status"]
            
            # Skip terminated employees
            if status == "Terminated":
                continue
                
            # Filter attendance for this employee in this month
            emp_att = df_att_month[df_att_month["employee_id"] == emp_id]
            
            # Count PTO, Sick Leave, and On Leave days
            # Note: Active employees On Leave status is in employee status, or we check attendance status
            leave_days = len(emp_att[emp_att["status"].isin(["PTO", "Sick Leave", "On Leave"])])
            
            # Standard hours
            std_hours = 8.0
            total_capacity = num_weekdays * std_hours
            
            # Available capacity = Total capacity minus leave hours
            # If the employee status is "On Leave", their available capacity should be 0.0
            if status == "On Leave":
                available = 0.0
            else:
                available = total_capacity - (leave_days * std_hours)
                available = max(0.0, available)
                
            capacity.append({
                "capacity_id": f"CAP{cap_id_counter:03d}",
                "employee_id": emp_id,
                "month": month,
                "working_days": num_weekdays,
                "standard_hours_per_day": std_hours,
                "total_capacity_hours": total_capacity,
                "available_hours": available
            })
            cap_id_counter += 1
            
    df_capacity = pd.DataFrame(capacity)
    capacity_path = get_dataset_path(CAPACITY_FILE)
    df_capacity.to_csv(capacity_path, index=False)
    print(f"Saved: {capacity_path} ({len(df_capacity)} rows)")
    print("Dataset generation completed successfully.")

if __name__ == "__main__":
    generate_datasets()
