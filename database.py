import pyodbc
from config import DB_CONFIG


def get_connection():
    conn_str = (
        f"DRIVER={{{DB_CONFIG['driver']}}};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        "Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)


def get_all_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Students")
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]


def get_student_by_id(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Students WHERE StudentID = ?", student_id)
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    conn.close()
    return dict(zip(columns, row)) if row else None


def get_students_by_major(major):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Students WHERE Major LIKE ?", f"%{major}%")
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]


def get_students_by_city(city):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Students WHERE City LIKE ?", f"%{city}%")
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]


def get_top_students(limit=3):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT TOP {limit} * FROM Students ORDER BY GPA DESC")
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]