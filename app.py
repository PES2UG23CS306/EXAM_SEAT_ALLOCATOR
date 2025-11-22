"""
Streamlit frontend for "Exam Hall Seat Allocator and Checker"
"""

import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import errorcode
from contextlib import contextmanager
from datetime import datetime
import os
from dotenv import load_dotenv
from io import StringIO

load_dotenv()  # optional .env

# ------------------ DB CONFIG MUST BE HERE ------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Likith#321",  
    "database": "exam_seat_allocator",
    "auth_plugin": "mysql_native_password"
}

st.write("ACTIVE DB CONFIG:", DB_CONFIG)
# ------------------------------------------------------------



@contextmanager
def get_conn():
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        yield conn
    except mysql.connector.Error as e:
        st.error(f"Database error: {e}")
        st.stop()
    finally:
        if conn:
            conn.close()

def run_select(query, params=None):
    with get_conn() as conn:
        df = pd.read_sql(query, conn, params=params)
    return df

def run_query(query, params=None, commit=True):
    """
    Execute a query (INSERT, UPDATE, DELETE, CALL procedure, etc.)
    Returns results for procedures, None for DML statements.
    """
    with get_conn() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params or ())
            
            # Check if it's a stored procedure call
            if query.strip().lower().startswith("call"):
                results = []
                
                # Fetch results from the first result set (if any)
                try:
                    results = cursor.fetchall()
                except mysql.connector.Error:
                    # No results in first set, that's okay
                    pass
                
                # CRITICAL: Consume all remaining result sets
                while cursor.nextset():
                    try:
                        cursor.fetchall()  # Consume but don't store
                    except mysql.connector.Error:
                        pass
                
                if commit:
                    conn.commit()
                
                return results if results else None
            
            else:
                # Regular DML query (INSERT, UPDATE, DELETE, DDL)
                if commit:
                    conn.commit()
                
                # Try to fetch results (for SELECT-like queries)
                try:
                    return cursor.fetchall()
                except mysql.connector.Error as e:
                    # Expected for INSERT/UPDATE/DELETE which don't return results
                    if e.errno == mysql.connector.errorcode.CR_NO_RESULT_SET:
                        return None
                    else:
                        raise
                        
        except mysql.connector.Error as e:
            st.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()


# ---------- HELPERS ----------
def reload_table(table_name):
    return run_select(f"SELECT * FROM {table_name} ORDER BY 1")

def safe_int(x):
    try:
        return int(x)
    except:
        return None

# ---------- UI: Sidebar Navigation ----------
st.sidebar.title("Exam Hall Seat Allocator")
page = st.sidebar.radio("Navigate", [
    "Home",
    "Students",
    "Exams",
    "Halls & Seats",
    "Invigilators",
    "Hall Assignments",
    "Allocations",
    "Seat Checks",
    "Auto-Allocate",
    "Seat Map",
    "Queries & Procedures",
    "Dashboard",
    "DB Admin"
])

# ---------- HOME ----------
if page == "Home":
    st.title("Exam Hall Seat Allocator — Streamlit Frontend")
    st.markdown("""
    **What this app provides**
    - CRUD operations for all tables
    - Auto allocation algorithm
    - Visual seat maps per hall & exam
    - Dashboard insights and CSV export
    """)
    st.markdown("**Database connection settings:**")
    st.write(DB_CONFIG)

# ---------- STUDENTS CRUD ----------
def students_ui():
    st.header("Students — CRUD")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Add student")
        with st.form("add_student"):
            sid = st.number_input("student_id (int)", min_value=1, step=1)
            srn = st.text_input("SRN")
            name = st.text_input("Full name")
            dept = st.text_input("Department", value="CSE")
            year = st.number_input("Year of study", min_value=1, max_value=8, value=2)
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            gender = st.selectbox("Gender", ["M", "F", "O"])
            dob = st.date_input("Date of birth")
            submitted = st.form_submit_button("Add student")
            if submitted:
                try:
                    q = """INSERT INTO students (student_id, srn, full_name, department, year_of_study, email, phone, gender, dob)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                    run_query(q, (sid, srn, name, dept, year, email or None, phone or None, gender, dob))
                    st.success("Student added")
                except Exception as e:
                    st.error(f"Error: {e}")
    with col2:
        st.subheader("Existing students")
        df = reload_table("students")
        st.dataframe(df)
        st.markdown("**Update / Delete**")
        sel = st.selectbox("Select student_id to edit/delete", options=[None]+df['student_id'].tolist())
        if sel:
            rec = df[df['student_id']==sel].iloc[0].to_dict()
            with st.form("edit_student"):
                name = st.text_input("Full name", value=rec.get('full_name',''))
                dept = st.text_input("Department", value=rec.get('department',''))
                year = st.number_input("Year of study", min_value=1, max_value=8, value=int(rec.get('year_of_study',1)))
                email = st.text_input("Email", value=rec.get('email') or "")
                phone = st.text_input("Phone", value=rec.get('phone') or "")
                gender = st.selectbox("Gender", ["M","F","O"], index=["M","F","O"].index(rec.get('gender','O')))
                submitted2 = st.form_submit_button("Update")
                if submitted2:
                    try:
                        q = """UPDATE students SET full_name=%s, department=%s, year_of_study=%s, email=%s, phone=%s, gender=%s WHERE student_id=%s"""
                        run_query(q, (name, dept, year, email or None, phone or None, gender, sel))
                        st.success("Updated")
                    except Exception as e:
                        st.error(f"Error: {e}")
            if st.button("Delete selected student"):
                try:
                    run_query("DELETE FROM students WHERE student_id=%s", (sel,))
                    st.success("Deleted")
                except Exception as e:
                    st.error(f"Error: {e}")

if page == "Students":
    students_ui()

# ---------- EXAMS CRUD ----------
def exams_ui():
    st.header("Exams — CRUD")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Add exam")
        with st.form("add_exam"):
            exam_id = st.number_input("exam_id", min_value=1, step=1)
            code = st.text_input("Course code")
            name = st.text_input("Course name")
            date = st.date_input("Exam date")
            start = st.time_input("Start time")
            end = st.time_input("End time")
            marks = st.number_input("Total marks", min_value=1, value=100)
            submitted = st.form_submit_button("Add exam")
            if submitted:
                try:
                    q = """INSERT INTO exams (exam_id, course_code, course_name, exam_date, start_time, end_time, total_marks)
                           VALUES (%s,%s,%s,%s,%s,%s,%s)"""
                    run_query(q, (exam_id, code, name, date, start, end, marks))
                    st.success("Exam added")
                except Exception as e:
                    st.error(f"Error: {e}")
    with col2:
        st.subheader("Existing exams")
        df = reload_table("exams")
        st.dataframe(df)
        sel = st.selectbox("Select exam_id to edit/delete", options=[None]+df['exam_id'].tolist())
        if sel:
            rec = df[df['exam_id']==sel].iloc[0].to_dict()
            with st.form("edit_exam"):
                code = st.text_input("Course code", value=rec.get('course_code',''))
                name = st.text_input("Course name", value=rec.get('course_name',''))
                date = st.date_input("Exam date", value=pd.to_datetime(rec.get('exam_date')).date())
                start = st.time_input("Start time", value=pd.to_datetime(str(rec.get('start_time'))).time())
                end = st.time_input("End time", value=pd.to_datetime(str(rec.get('end_time'))).time())
                marks = st.number_input("Total marks", min_value=1, value=int(rec.get('total_marks',100)))
                submitted2 = st.form_submit_button("Update exam")
                if submitted2:
                    try:
                        q = """UPDATE exams SET course_code=%s, course_name=%s, exam_date=%s, start_time=%s, end_time=%s, total_marks=%s WHERE exam_id=%s"""
                        run_query(q, (code, name, date, start, end, marks, sel))
                        st.success("Updated")
                    except Exception as e:
                        st.error(f"Error: {e}")
            if st.button("Delete selected exam"):
                try:
                    run_query("DELETE FROM exams WHERE exam_id=%s", (sel,))
                    st.success("Deleted")
                except Exception as e:
                    st.error(f"Error: {e}")

if page == "Exams":
    exams_ui()

# ---------- HALLS & SEATS ----------
def halls_seats_ui():
    st.header("Halls & Seats")
    c1, c2 = st.columns([1,2])
    with c1:
        st.subheader("Add hall")
        with st.form("add_hall"):
            hid = st.number_input("hall_id", min_value=1)
            name = st.text_input("Hall name")
            capacity = st.number_input("Capacity", min_value=1, value=30)
            loc = st.text_input("Location")
            sub = st.form_submit_button("Add hall")
            if sub:
                try:
                    run_query("INSERT INTO halls (hall_id, hall_name, capacity, location) VALUES (%s,%s,%s,%s)",
                              (hid, name, capacity, loc or None))
                    st.success("Hall added")
                except Exception as e:
                    st.error(f"Error: {e}")
        st.subheader("Add seat")
        with st.form("add_seat"):
            sid = st.number_input("seat_id", min_value=1, step=1, key="seat_id")
            hall_choices = reload_table("halls")
            hall_options = hall_choices['hall_id'].tolist()
            hall_sel = st.selectbox("Select hall_id", options=[None]+hall_options)
            seat_num = st.text_input("Seat number (e.g. A1)")
            accessible = st.checkbox("Accessible")
            remarks = st.text_input("Remarks")
            sub2 = st.form_submit_button("Add seat")
            if sub2:
                try:
                    run_query("""INSERT INTO seats (seat_id, hall_id, seat_number, is_accessible, remarks)
                                 VALUES (%s,%s,%s,%s,%s)""",
                              (sid, hall_sel, seat_num, int(accessible), remarks or None))
                    st.success("Seat added")
                except Exception as e:
                    st.error(f"Error: {e}")

    with c2:
        st.subheader("Halls table")
        st.dataframe(reload_table("halls"))
        st.subheader("Seats table")
        st.dataframe(reload_table("seats"))

        st.markdown("**Edit or delete seat**")
        seats_df = reload_table("seats")
        sel = st.selectbox("Select seat_id", options=[None]+seats_df['seat_id'].tolist())
        if sel:
            rec = seats_df[seats_df['seat_id']==sel].iloc[0].to_dict()
            with st.form("edit_seat"):
                seat_number = st.text_input("Seat number", value=rec.get('seat_number'))
                is_access = st.checkbox("Accessible", value=bool(rec.get('is_accessible')))
                remarks = st.text_input("Remarks", value=rec.get('remarks') or "")
                submitted = st.form_submit_button("Update seat")
                if submitted:
                    try:
                        run_query("UPDATE seats SET seat_number=%s, is_accessible=%s, remarks=%s WHERE seat_id=%s",
                                  (seat_number, int(is_access), remarks or None, sel))
                        st.success("Updated")
                    except Exception as e:
                        st.error(f"Error: {e}")
            if st.button("Delete seat"):
                try:
                    run_query("DELETE FROM seats WHERE seat_id=%s", (sel,))
                    st.success("Deleted")
                except Exception as e:
                    st.error(f"Error: {e}")

if page == "Halls & Seats":
    halls_seats_ui()

# ---------- INVIGILATORS ----------
def invigilators_ui():
    st.header("Invigilators")
    left, right = st.columns(2)
    with left:
        st.subheader("Add Invigilator")
        with st.form("add_inv"):
            iid = st.number_input("invigilator_id", min_value=1)
            name = st.text_input("Full name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            assigned = st.checkbox("Assigned", value=False)
            sub = st.form_submit_button("Add")
            if sub:
                try:
                    run_query("INSERT INTO invigilators (invigilator_id, full_name, email, phone, assigned) VALUES (%s,%s,%s,%s,%s)",
                              (iid, name, email or None, phone or None, int(assigned)))
                    st.success("Added")
                except Exception as e:
                    st.error(f"Error: {e}")
    with right:
        st.subheader("Existing invigilators")
        st.dataframe(reload_table("invigilators"))
        df = reload_table("invigilators")
        sel = st.selectbox("Select invigilator_id", options=[None]+df['invigilator_id'].tolist())
        if sel:
            rec = df[df['invigilator_id']==sel].iloc[0].to_dict()
            with st.form("edit_inv"):
                name = st.text_input("Full name", value=rec.get('full_name'))
                email = st.text_input("Email", value=rec.get('email') or "")
                phone = st.text_input("Phone", value=rec.get('phone') or "")
                assigned = st.checkbox("Assigned", value=bool(rec.get('assigned')))
                sub2 = st.form_submit_button("Update")
                if sub2:
                    try:
                        run_query("UPDATE invigilators SET full_name=%s, email=%s, phone=%s, assigned=%s WHERE invigilator_id=%s",
                                  (name, email or None, phone or None, int(assigned), sel))
                        st.success("Updated")
                    except Exception as e:
                        st.error(f"Error: {e}")
            if st.button("Delete invigilator"):
                try:
                    run_query("DELETE FROM invigilators WHERE invigilator_id=%s", (sel,))
                    st.success("Deleted")
                except Exception as e:
                    st.error(f"Error: {e}")

if page == "Invigilators":
    invigilators_ui()

# ---------- HALL ASSIGNMENTS ----------
def hall_assignments_ui():
    st.header("Hall Assignments (Link exam <-> hall)")
    df_exams = reload_table("exams")
    df_halls = reload_table("halls")
    df_inv = reload_table("invigilators")

    with st.form("add_assignment"):
        aid = st.number_input("assignment_id", min_value=1)
        exam_sel = st.selectbox("Exam", options=[None]+df_exams['exam_id'].tolist())
        hall_sel = st.selectbox("Hall", options=[None]+df_halls['hall_id'].tolist())
        inv_sel = st.selectbox("Invigilator (optional)", options=[None]+df_inv['invigilator_id'].tolist())
        start = st.time_input("Start time")
        end = st.time_input("End time")
        sub = st.form_submit_button("Add assignment")
        if sub:
            try:
                run_query("""INSERT INTO hall_assignments (assignment_id, exam_id, hall_id, invigilator_id, start_time, end_time)
                             VALUES (%s,%s,%s,%s,%s,%s)""",
                          (aid, exam_sel, hall_sel, inv_sel, start, end))
                st.success("Assignment added")
            except Exception as e:
                st.error(f"Error: {e}")

    st.subheader("Existing assignments")
    st.dataframe(reload_table("hall_assignments"))

if page == "Hall Assignments":
    hall_assignments_ui()

# ---------- ALLOCATIONS CRUD & ALLOCATION VIEW ----------
def allocations_ui():
    st.header("Allocations")
    st.markdown("Manual allocate student to seat for an exam (CRUD)")
    df_exams = reload_table("exams")
    with st.form("manual_alloc"):
        alloc_id = st.number_input("allocation_id", min_value=1)
        exam_sel = st.selectbox("Exam", options=[None]+df_exams['exam_id'].tolist(), key="alloc_exam")
        students = reload_table("students")
        student_sel = st.selectbox("Student (optional)", options=[None]+students['student_id'].tolist())
        seats_all = reload_table("seats")
        seat_sel = st.selectbox("Seat", options=[None]+seats_all['seat_id'].tolist())
        sub = st.form_submit_button("Create allocation")
        if sub:
            try:
                run_query("INSERT INTO allocations (allocation_id, exam_id, student_id, seat_id) VALUES (%s,%s,%s,%s)",
                          (alloc_id, exam_sel, student_sel, seat_sel))
                st.success("Allocated")
            except Exception as e:
                st.error(f"Error: {e}")

    st.subheader("Existing allocations")
    allocs = reload_table("allocations")
    st.dataframe(allocs)

    sel = st.selectbox("Select allocation_id to delete", options=[None]+allocs['allocation_id'].tolist())
    if sel and st.button("Delete allocation"):
        try:
            run_query("DELETE FROM allocations WHERE allocation_id=%s", (sel,))
            st.success("Deleted")
        except Exception as e:
            st.error(f"Error: {e}")

if page == "Allocations":
    allocations_ui()

# ---------- SEAT CHECKS ----------
def seat_checks_ui():
    st.header("Seat Checks (invigilator checks)")
    st.subheader("Add seat check record")
    df_allocs = reload_table("allocations")
    df_inv = reload_table("invigilators")
    with st.form("add_check"):
        cid = st.number_input("check_id", min_value=1)
        alloc_sel = st.selectbox("Allocation", options=[None]+df_allocs['allocation_id'].tolist())
        inv_sel = st.selectbox("Checked by (invigilator)", options=[None]+df_inv['invigilator_id'].tolist())
        status = st.selectbox("Status", ["OK","MISMATCH","ABSENT","OTHER"])
        remarks = st.text_input("Remarks")
        sub = st.form_submit_button("Add check")
        if sub:
            try:
                run_query("INSERT INTO seat_checks (check_id, allocation_id, checked_by, status, remarks) VALUES (%s,%s,%s,%s,%s)",
                          (cid, alloc_sel, inv_sel, status, remarks or None))
                st.success("Added")
            except Exception as e:
                st.error(f"Error: {e}")

    st.subheader("Existing seat checks")
    st.dataframe(reload_table("seat_checks"))

if page == "Seat Checks":
    seat_checks_ui()

# ---------- AUTO-ALLOCATION ALGORITHM ----------
def auto_allocate_ui():
    st.header("Auto-Allocate Seats for an Exam")
    st.markdown("Greedy allocator: assigns unallocated students to free seats in halls assigned for the exam. Respects unique constraints (one seat per student & one allocation per seat per exam).")
    exams = reload_table("exams")
    exam_choices = exams['exam_id'].tolist()
    exam_selected = st.selectbox("Choose exam_id to auto-allocate", options=[None]+exam_choices)

    if exam_selected:
        st.write("Exam details:")
        st.table(exams[exams['exam_id']==exam_selected])
        if st.button("Simulate allocation (show how many will be allocated)"):
            # compute unallocated students and free seats
            q_unallocated = """
                SELECT s.student_id FROM students s
                WHERE s.student_id NOT IN (SELECT student_id FROM allocations WHERE exam_id = %s)
                ORDER BY s.student_id
            """
            q_free_seats = """
                SELECT seat_id, hall_id, seat_number FROM seats
                WHERE seat_id NOT IN (SELECT seat_id FROM allocations WHERE exam_id = %s)
                AND hall_id IN (SELECT hall_id FROM hall_assignments WHERE exam_id = %s)
                ORDER BY hall_id, seat_number
            """
            students = run_select(q_unallocated, params=(exam_selected,))
            seats = run_select(q_free_seats, params=(exam_selected, exam_selected))
            st.write(f"Unallocated students count: {len(students)}")
            st.write(f"Available seats in assigned halls: {len(seats)}")
            st.dataframe(students)
            st.dataframe(seats)
        if st.button("Run auto-allocate now"):
            # run allocation in a transaction, assign sequentially
            q_students = "SELECT student_id FROM students WHERE student_id NOT IN (SELECT student_id FROM allocations WHERE exam_id=%s) ORDER BY student_id"
            q_seats = """SELECT seat_id FROM seats
                         WHERE seat_id NOT IN (SELECT seat_id FROM allocations WHERE exam_id=%s)
                         AND hall_id IN (SELECT hall_id FROM hall_assignments WHERE exam_id = %s)
                         ORDER BY hall_id, seat_number"""
            studs = run_select(q_students, params=(exam_selected,))
            seats = run_select(q_seats, params=(exam_selected, exam_selected))
            studs_list = studs['student_id'].tolist()
            seats_list = seats['seat_id'].tolist()
            if not seats_list:
                st.warning("No free seats available for this exam's assigned halls.")
            if not studs_list:
                st.info("No unallocated students for this exam.")
            allocate_count = min(len(studs_list), len(seats_list))
            if allocate_count == 0:
                st.stop()
            # insert allocations with next available allocation_id
            next_alloc_q = "SELECT COALESCE(MAX(allocation_id), 0) + 1 FROM allocations"
            next_alloc_id = run_select(next_alloc_q).iloc[0,0]
            params = []
            for i in range(allocate_count):
                params.append((next_alloc_id + i, exam_selected, studs_list[i], seats_list[i]))
            try:
                # bulk insert
                with get_conn() as conn:
                    cur = conn.cursor()
                    cur.executemany("INSERT INTO allocations (allocation_id, exam_id, student_id, seat_id) VALUES (%s,%s,%s,%s)", params)
                    conn.commit()
                st.success(f"Allocated {allocate_count} students.")
            except Exception as e:
                st.error(f"Error during allocation: {e}")

if page == "Auto-Allocate":
    auto_allocate_ui()

# ---------- VISUAL SEAT MAP ----------
def seat_map_ui():
    st.header("Seat Map for a Hall & Exam")
    halls = reload_table("halls")
    exams = reload_table("exams")
    hall_sel = st.selectbox("Select hall_id", options=[None]+halls['hall_id'].tolist())
    exam_sel = st.selectbox("Select exam_id (to show allocated students)", options=[None]+exams['exam_id'].tolist())

    if hall_sel:
        seats = run_select("SELECT seat_id, seat_number, is_accessible FROM seats WHERE hall_id=%s ORDER BY seat_number", params=(hall_sel,))
        if seats.empty:
            st.info("No seats in this hall.")
            st.stop()
        # fetch allocations for this exam & hall
        if exam_sel:
            allocs_q = """SELECT a.allocation_id, a.seat_id, a.student_id, s.srn, s.full_name
                          FROM allocations a
                          LEFT JOIN students s ON a.student_id = s.student_id
                          JOIN seats se ON a.seat_id = se.seat_id
                          WHERE a.exam_id=%s AND se.hall_id=%s"""
            allocs = run_select(allocs_q, params=(exam_sel, hall_sel))
            alloc_map = {row['seat_id']: row for _, row in allocs.iterrows()}
        else:
            alloc_map = {}

        st.write("Seat layout (simple list) — click to view details in table below")
        # create a grid with 6 seats per row visually using columns
        seat_list = seats.to_dict('records')
        per_row = 6
        rows = [seat_list[i:i+per_row] for i in range(0, len(seat_list), per_row)]
        for r in rows:
            cols = st.columns(len(r))
            for c, seat in zip(cols, r):
                sid = seat['seat_id']
                slabel = seat['seat_number']
                allocated = sid in alloc_map
                label = f"{slabel}\n({'A' if allocated else 'Free'})"
                if allocated:
                    student = alloc_map[sid]
                    c.button(label, key=f"seat_{sid}", help=f"Allocated to: {student.get('full_name')} ({student.get('srn')})")
                else:
                    c.button(label, key=f"seat_free_{sid}")

        st.subheader("Seat detail table")
        display = seats.merge(allocs[['seat_id','student_id','srn','full_name']], how='left', on='seat_id')
        st.dataframe(display)

if page == "Seat Map":
    seat_map_ui()

# ---------- QUERIES & PROCEDURES ----------
def procedures_ui():
    st.header("Queries & Procedures")
    st.markdown("You can run ad-hoc SELECT queries (read-only) and 'procedures' we create.")
    st.subheader("Run a SELECT query")
    qtext = st.text_area("SELECT query", value="SELECT * FROM allocations LIMIT 100")
    if st.button("Run SELECT"):
        if not qtext.strip().lower().startswith("select"):
            st.error("Only SELECT queries allowed here.")
        else:
            try:
                df = run_select(qtext)
                st.dataframe(df)
            except Exception as e:
                st.error(f"Error: {e}")

    
    st.markdown("---")
    st.subheader("Call Custom Stored Procedures")

    # --- UI for allocate_student_to_seat ---
    st.markdown("#### 1. Allocate Student to Seat")
    st.write("Calls `allocate_student_to_seat(exam, student, seat)` [cite: 91]")
    with st.form("call_alloc_proc"):
        p_exam_id = st.number_input("Exam ID", min_value=1, step=1)
        p_student_id = st.number_input("Student ID", min_value=1, step=1)
        p_seat_id = st.number_input("Seat ID", min_value=1, step=1)
        
        submitted_alloc = st.form_submit_button("Run Procedure")
        if submitted_alloc:
            try:
                sql = "CALL allocate_student_to_seat(%s, %s, %s)"
                # run_query returns a list of tuples, e.g., [('Allocation Successful',)]
                result = run_query(sql, (p_exam_id, p_student_id, p_seat_id))
                st.success(result[0][0]) # Display the message from the procedure [cite: 110, 112]
            except Exception as e:
                st.error(f"Error calling procedure: {e}")

    # --- UI for remove_allocation ---
    st.markdown("#### 2. Remove Allocation")
    st.write("Calls `remove_allocation(allocation_id)` [cite: 175]")
    with st.form("call_remove_proc"):
        p_alloc_id = st.number_input("Allocation ID to Remove", min_value=1, step=1)
        
        submitted_remove = st.form_submit_button("Run Procedure")
        if submitted_remove:
            try:
                sql = "CALL remove_allocation(%s)"
                result = run_query(sql, (p_alloc_id,))
                st.success(result[0][0]) # Display the message [cite: 178, 204]
            except Exception as e:
                st.error(f"Error calling procedure: {e}")
    st.markdown("---")
    st.subheader("Call Custom Functions")

    # --- UI for count_allocated_students ---
    st.markdown("#### 1. Count Allocated Students")
    st.write("Calls `count_allocated_students(exam_id)` [cite: 212]")
    with st.form("call_count_fn"):
        p_exam_id_fn = st.number_input("Exam ID", min_value=1, step=1, key="fn1_exam")
        submitted_count = st.form_submit_button("Run Function")
        if submitted_count:
            try:
                sql = "SELECT count_allocated_students(%s) AS 'Total Students'"
                df = run_select(sql, (p_exam_id_fn,))
                st.dataframe(df) # Will show the result, e.g., 4 [cite: 248]
            except Exception as e:
                st.error(f"Error calling function: {e}")

    # --- UI for hall_occupancy ---
    st.markdown("#### 2. Get Hall Occupancy")
    st.write("Calls `hall_occupancy(exam_id, hall_id)` [cite: 252]")
    with st.form("call_occupancy_fn"):
        p_exam_id_fn2 = st.number_input("Exam ID", min_value=1, step=1, key="fn2_exam")
        p_hall_id_fn2 = st.number_input("Hall ID", min_value=1, step=1, key="fn2_hall")
        submitted_occ = st.form_submit_button("Run Function")
        if submitted_occ:
            try:
                sql = "SELECT hall_occupancy(%s, %s) AS 'Occupancy %%'"
                df = run_select(sql, (p_exam_id_fn2, p_hall_id_fn2))
                st.dataframe(df) # Will show the result, e.g., 80.00 [cite: 317]
            except Exception as e:
                st.error(f"Error calling function: {e}")

    # --- UI for get_student_seat ---
    st.markdown("#### 3. Get Student Seat by SRN")
    st.write("Calls `get_student_seat(srn)` [cite: 322]")
    with st.form("call_seat_fn"):
        p_srn = st.text_input("Student SRN (e.g., PES2UG23CS101)")
        submitted_seat = st.form_submit_button("Run Function")
        if submitted_seat and p_srn:
            try:
                sql = "SELECT get_student_seat(%s) AS 'Seat Info'"
                df = run_select(sql, (p_srn,))
                st.dataframe(df) # Will show the result, e.g., 'LH-101 A1' [cite: 378]
            except Exception as e:
                st.error(f"Error calling function: {e}")

if page == "Queries & Procedures":
    procedures_ui()

# ---------- DASHBOARD ----------
def dashboard_ui():
    st.header("Dashboard")
    st.subheader("Seats filled per hall (all exams combined)")
    q = """
    SELECT h.hall_name, COUNT(a.allocation_id) AS filled
    FROM halls h
    LEFT JOIN seats s ON s.hall_id = h.hall_id
    LEFT JOIN allocations a ON a.seat_id = s.seat_id
    GROUP BY h.hall_name
    """
    df = run_select(q)
    if not df.empty:
        st.bar_chart(df.set_index('hall_name'))
    else:
        st.write("No data yet.")

    st.subheader("Students per exam")
    q2 = """SELECT e.course_code, COUNT(a.allocation_id) AS allocated
            FROM exams e
            LEFT JOIN allocations a ON a.exam_id = e.exam_id
            GROUP BY e.course_code"""
    df2 = run_select(q2)
    st.bar_chart(df2.set_index('course_code'))

if page == "Dashboard":
    dashboard_ui()


# ---------- DB ADMIN (USERS & TRIGGERS) ----------
def db_admin_ui():
    st.header("Database Administration")
    st.warning("⚠️ These operations are for high-level database admins only.")
    st.markdown(f"You are connected as user **{DB_CONFIG.get('user')}**. This user must have permissions like `CREATE USER` and `GRANT OPTION` for this page to work.")
    
    db_name = DB_CONFIG.get('database')
    
    tab1, tab2 = st.tabs(["User Management", "Trigger Management"])

    with tab1:
        # --- User Management ---
        st.subheader("User Management")
        
        try:
            # Filter out system users
            current_app_user = DB_CONFIG.get('user')
            q_users = f"""
                SELECT user, host FROM mysql.user 
                WHERE user NOT LIKE 'mysql.%' 
                AND user NOT LIKE 'root' 
                AND user NOT LIKE 'debian-%'
                AND user != %s
            """
            users_df = run_select(q_users, params=(current_app_user,))
            st.dataframe(users_df)
            user_list = [f"'{row.user}'@'{row.host}'" for i, row in users_df.iterrows()]
        except Exception as e:
            st.error(f"Could not list users. Ensure '{current_app_user}' has permission to read `mysql.user`. Error: {e}")
            st.stop() 

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Create New User")
            with st.form("create_user"):
                username = st.text_input("New Username")
                password = st.text_input("New Password", type="password")
                host = st.text_input("Host", value="localhost")
                sub_create = st.form_submit_button("Create User")
                
                if sub_create and username and password:
                    try:
                        # f-string is necessary for DDL like CREATE USER
                        run_query(f"CREATE USER '{username}'@'{host}' IDENTIFIED BY %s", (password,))
                        st.success(f"User '{username}'@'{host}' created.")
                    except Exception as e:
                        st.error(f"Error creating user: {e}")
        
        with c2:
            st.markdown("#### Drop User")
            user_to_drop = st.selectbox("Select user to drop", [None] + user_list, key="drop_user_select")
            if user_to_drop and st.button("DROP USER", key="drop_user_btn"):
                try:
                    run_query(f"DROP USER {user_to_drop}") # DDL
                    st.success(f"User {user_to_drop} dropped.")
                except Exception as e:
                    st.error(f"Error dropping user: {e}")

        st.markdown("---")
        st.markdown("#### Manage Privileges")
        user_to_grant = st.selectbox("Select user to manage", [None] + user_list, key="grant_user_select")
        
        if user_to_grant:
            st.write(f"Managing privileges for **{user_to_grant}** on database `{db_name}`")
            
            priv_type = st.selectbox("Select Privilege Level", ["Read-Only (SELECT)", "Read-Write (SELECT, INSERT, UPDATE, DELETE)"])

            col_g1, col_g2 = st.columns(2)
            with col_g1:
                if st.button("GRANT Privileges"):
                    try:
                        grant_sql = ""
                        if priv_type.startswith("Read-Only"):
                            grant_sql = f"GRANT SELECT ON {db_name}.* TO {user_to_grant}"
                        elif priv_type.startswith("Read-Write"):
                            grant_sql = f"GRANT SELECT, INSERT, UPDATE, DELETE ON {db_name}.* TO {user_to_grant}"
                        run_query(grant_sql)
                        st.success(f"Privileges granted to {user_to_grant}")
                    except Exception as e:
                        st.error(f"Error granting privileges: {e}")
            with col_g2:
                if st.button("REVOKE All Privileges"):
                    try:
                        run_query(f"REVOKE ALL PRIVILEGES ON {db_name}.* FROM {user_to_grant}")
                        st.success(f"All privileges revoked from {user_to_grant} on {db_name}.")
                    except Exception as e:
                        st.error(f"Error revoking privileges: {e}")

            st.markdown("##### Current Grants")
            try:
                grants = run_query(f"SHOW GRANTS FOR {user_to_grant}", commit=False)
                st.code('\n'.join([g[0] for g in grants]), language="sql")
            except Exception as e:
                st.error(f"Could not show grants: {e}")
    
    with tab2:
        # --- Trigger Management ---
        st.subheader("Trigger Management")
        st.markdown(f"View, Drop, and Create triggers in the `{db_name}` database.")

        # View Triggers
        st.markdown("#### Existing Triggers")
        try:
            triggers_df = run_select(f"SHOW TRIGGERS FROM {db_name}")
            if triggers_df.empty:
                st.info("No triggers found in this database.")
            else:
                st.dataframe(triggers_df)
                
                trigger_list = triggers_df['Trigger'].tolist()
                trigger_to_view = st.selectbox("Select trigger to view or drop", [None] + trigger_list)
                
                if trigger_to_view:
                    st.markdown("##### View Trigger Code")
                    try:
                        # SHOW CREATE TRIGGER returns a table, code is at [0][2]
                        trigger_code_result = run_query(f"SHOW CREATE TRIGGER {trigger_to_view}", commit=False)
                        st.code(trigger_code_result[0][2], language="sql") 
                    except Exception as e:
                        st.error(f"Could not get trigger code: {e}")
                    
                    st.markdown("##### Drop Trigger")
                    if st.button("DROP TRIGGER", key="drop_trigger_btn"):
                        try:
                            run_query(f"DROP TRIGGER {trigger_to_view}")
                            st.success(f"Trigger {trigger_to_view} dropped.")
                        except Exception as e:
                            st.error(f"Error dropping trigger: {e}")
        except Exception as e:
            st.error(f"Could not list triggers: {e}")

        # Create Trigger
        st.markdown("---")
        st.markdown("#### Create New Trigger")
        st.info("Note: Creating triggers requires precise SQL. This form does not support changing the DELIMITER, so complex triggers with semicolons in the body may fail.")
        with st.form("create_trigger"):
            trigger_sql = st.text_area("Full CREATE TRIGGER statement", height=300, placeholder="CREATE TRIGGER my_trigger...")
            sub_trigger = st.form_submit_button("Run CREATE TRIGGER statement")
            if sub_trigger and trigger_sql:
                try:
                    # This is a direct query.
                    run_query(trigger_sql)
                    st.success("Trigger creation statement executed.")
                except Exception as e:
                    st.error(f"Error creating trigger: {e}")
if page == "Export":
    export_ui()

# ---------- ADD THIS BLOCK ----------
if page == "DB Admin":
    db_admin_ui()
# ------------------------------------

# ---------- QUERIES: General safety ----------
# NOTE: For the purposes of the assignment we allow running only SELECT query from the Queries page.

# ---------- QUERIES: General safety ----------
# NOTE: For the purposes of the assignment we allow running only SELECT query from the Queries page.
# You can create stored procedures in MySQL directly (DDL) and invoke them via this UI by adding a run_query call.

# ---------- END ----------
st.sidebar.markdown("---")
st.sidebar.write("Project: Exam Hall Seat Allocator")
st.sidebar.write("Team: PES2UG23CS275, PES2UG23CS306")
st.sidebar.write("Guidelines: CRUD, Procedures, Triggers, Complex queries, Dashboard, Standalone/web app")
