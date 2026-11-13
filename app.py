from datetime import date, datetime
import os

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admission_no = db.Column(db.String(30), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    grade = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Active")


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    teacher = db.Column(db.String(120), nullable=False)


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    day = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), nullable=False)
    student = db.relationship("Student")


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    course = db.relationship("Course")


def make_app():
    app = Flask(__name__)
    database_url = os.getenv("DATABASE_URL", "sqlite:///school_demo.db")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
        seed_demo_data()

    @app.get("/")
    def dashboard():
        today = date.today()
        return render_template(
            "dashboard.html",
            student_count=Student.query.filter_by(status="Active").count(),
            course_count=Course.query.count(),
            attendance_today=Attendance.query.filter_by(day=today).count(),
            assignment_count=Assignment.query.count(),
            students=Student.query.order_by(Student.last_name).limit(5).all(),
            assignments=Assignment.query.order_by(Assignment.due_date).limit(5).all(),
        )

    @app.get("/students")
    def students():
        return render_template("students.html", students=Student.query.order_by(Student.last_name).all())

    @app.get("/attendance")
    def attendance():
        records = Attendance.query.order_by(Attendance.day.desc(), Attendance.id.desc()).limit(30).all()
        return render_template("attendance.html", students=Student.query.order_by(Student.last_name).all(), records=records)

    @app.post("/attendance")
    def mark_attendance():
        student = db.session.get(Student, request.form.get("student_id", type=int))
        status = request.form.get("status", "")
        day_text = request.form.get("day", "")
        try:
            record_day = datetime.strptime(day_text, "%Y-%m-%d").date()
        except ValueError:
            record_day = date.today()
        if student and status in {"Present", "Absent", "Late", "Excused"}:
            db.session.add(Attendance(student=student, day=record_day, status=status))
            db.session.commit()
        return redirect(url_for("attendance"))

    @app.get("/courses")
    def courses():
        return render_template("courses.html", courses=Course.query.order_by(Course.code).all())

    @app.get("/assignments")
    def assignments():
        items = Assignment.query.order_by(Assignment.due_date).all()
        return render_template("assignments.html", assignments=items, courses=Course.query.order_by(Course.code).all())

    @app.post("/assignments")
    def add_assignment():
        title = request.form.get("title", "").strip()
        course = db.session.get(Course, request.form.get("course_id", type=int))
        try:
            due_date = datetime.strptime(request.form.get("due_date", ""), "%Y-%m-%d").date()
        except ValueError:
            due_date = None
        if title and course and due_date:
            db.session.add(Assignment(title=title, course=course, due_date=due_date))
            db.session.commit()
        return redirect(url_for("assignments"))

    return app


def seed_demo_data():
    if Student.query.first():
        return
    students = [
        Student(admission_no="DEMO-1001", first_name="Jordan", last_name="Lee", grade="Grade 10"),
        Student(admission_no="DEMO-1002", first_name="Sam", last_name="Patel", grade="Grade 9"),
        Student(admission_no="DEMO-1003", first_name="Taylor", last_name="Morgan", grade="Grade 11"),
        Student(admission_no="DEMO-1004", first_name="Alex", last_name="Rivera", grade="Grade 10"),
    ]
    courses = [
        Course(code="MATH-10", title="Mathematics", teacher="Morgan Chen"),
        Course(code="SCI-10", title="General Science", teacher="Casey Brooks"),
        Course(code="ENG-09", title="English Language", teacher="Jamie Taylor"),
    ]
    db.session.add_all(students + courses)
    db.session.flush()
    db.session.add_all([
        Attendance(student=students[0], day=date.today(), status="Present"),
        Attendance(student=students[1], day=date.today(), status="Late"),
        Assignment(title="Algebra practice", course=courses[0], due_date=date.today()),
        Assignment(title="Science lab report", course=courses[1], due_date=date.today()),
        Assignment(title="Reading response", course=courses[2], due_date=date.today()),
    ])
    db.session.commit()


app = make_app()

if __name__ == "__main__":
    app.run(debug=True)
