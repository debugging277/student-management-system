from flask import Flask, render_template, request, redirect, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "student-management-secret-key"


def get_db_connection():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    return connection


@app.route("/")
def home():
    connection = get_db_connection()

    search = request.args.get("search", "").strip()

    if search:
        students = connection.execute("""
            SELECT * FROM students
            WHERE name LIKE ? OR roll_no LIKE ?
            ORDER BY id DESC
        """, ('%' + search + '%', '%' + search + '%')).fetchall()
    else:
        students = connection.execute(
            "SELECT * FROM students ORDER BY id DESC"
        ).fetchall()

    total_students = connection.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    total_courses = connection.execute(
        "SELECT COUNT(DISTINCT course) FROM students"
    ).fetchone()[0]

    average_marks = connection.execute(
        "SELECT AVG(marks) FROM students"
    ).fetchone()[0]

    connection.close()

    return render_template(
        "index.html",
        students=students,
        total_students=total_students,
        total_courses=total_courses,
        average_marks=average_marks,
        search=search
    )


@app.route("/add", methods=["POST"])
def add_student():
    roll_no = request.form["roll_no"].strip()
    name = request.form["name"].strip()
    age = request.form["age"]
    gender = request.form["gender"]
    course = request.form["course"].strip()
    email = request.form["email"].strip()
    phone = request.form["phone"].strip()
    marks = request.form["marks"]

    try:
        age_value = int(age)
        marks_value = float(marks)

        if age_value <= 0 or age_value > 120:
            raise ValueError

        if not 0 <= marks_value <= 100:
            raise ValueError

        if not roll_no or not name or not course:
            flash("Please fill all required fields.")
            return redirect("/")

    except ValueError:
        flash("Please enter valid age and marks (0–100).")
        return redirect("/")

    connection = get_db_connection()

    try:
        connection.execute("""
            INSERT INTO students
            (roll_no, name, age, gender, course, email, phone, marks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            roll_no, name, age_value, gender,
            course, email, phone, marks_value
        ))

        connection.commit()
        flash("Student added successfully!")

    except sqlite3.IntegrityError:
        flash("This Roll Number already exists.")

    finally:
        connection.close()

    return redirect("/")


@app.route("/edit/<int:student_id>")
def edit_student(student_id):
    connection = get_db_connection()

    student = connection.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    connection.close()

    if student is None:
        return "Student not found", 404

    return render_template("edit.html", student=student)


@app.route("/update/<int:student_id>", methods=["POST"])
def update_student(student_id):
    name = request.form["name"].strip()
    age = request.form["age"]

    try:
        age_value = int(age)

        if age_value <= 0 or age_value > 120:
            raise ValueError

    except ValueError:
        flash("Please enter a valid age.")
        return redirect(f"/edit/{student_id}")

    connection = get_db_connection()

    connection.execute("""
        UPDATE students
        SET name = ?, age = ?
        WHERE id = ?
    """, (name, age_value, student_id))

    connection.commit()
    connection.close()

    flash("Student updated successfully!")
    return redirect("/")


@app.route("/delete/<int:student_id>")
def delete_student(student_id):
    connection = get_db_connection()

    connection.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    connection.commit()
    connection.close()

    flash("Student deleted successfully!")
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)