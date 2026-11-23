"""StudentHub desktop application: Python, CustomTkinter and MySQL."""
import os
import re
import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "studentapp"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "student_management"),
}


class Database:
    def __init__(self):
        self.connection = mysql.connector.connect(**DB_CONFIG)
        with self.connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    roll_no VARCHAR(30) NOT NULL UNIQUE,
                    email VARCHAR(120),
                    phone VARCHAR(20),
                    course VARCHAR(100),
                    semester TINYINT UNSIGNED,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP
                )
            """)
        self.connection.commit()

    def fetch(self, query, params=()):
        with self.connection.cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def execute(self, query, params=()):
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.lastrowid

    def close(self):
        if self.connection.is_connected():
            self.connection.close()


class StudentHub(ctk.CTk):
    BG = "#0B1220"
    PANEL = "#111C30"
    CARD = "#172338"
    BLUE = "#2563EB"
    GREEN = "#059669"
    RED = "#DC2626"

    def __init__(self):
        super().__init__()
        self.title("StudentHub | Student Management System")
        self.geometry("1240x790")
        self.minsize(1000, 650)
        self.configure(fg_color=self.BG)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.selected_id = None
        self.entries = {}

        try:
            self.db = Database()
        except Error as exc:
            messagebox.showerror(
                "MySQL connection error",
                f"Could not connect to MySQL. Check that the service is running "
                f"and DB_* settings are correct.\n\nDetails: {exc}",
            )
            self.destroy()
            return

        self.build_ui()
        self.load_students()
        self.protocol("WM_DELETE_WINDOW", self.close_app)

    def build_ui(self):
        sidebar = ctk.CTkFrame(self, width=215, corner_radius=0, fg_color=self.PANEL)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        ctk.CTkLabel(
            sidebar, text="StudentHub", font=("Segoe UI", 23, "bold"),
            text_color="#60A5FA"
        ).pack(anchor="w", padx=20, pady=(30, 5))
        ctk.CTkLabel(
            sidebar, text="STUDENT MANAGEMENT", text_color="#71829D",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=22, pady=(0, 28))

        for label, command in (
            ("Dashboard", self.refresh_dashboard),
            ("Add Student", self.clear_form),
            ("Refresh Records", self.load_students),
        ):
            ctk.CTkButton(
                sidebar, text=label, command=command, anchor="w", height=42,
                fg_color="transparent", hover_color="#243650"
            ).pack(fill="x", padx=12, pady=4)

        ctk.CTkLabel(
            sidebar, text="Python • CustomTkinter • MySQL",
            text_color="#64748B", font=("Segoe UI", 9)
        ).pack(side="bottom", pady=22)

        main = ctk.CTkFrame(self, fg_color=self.BG, corner_radius=0)
        main.pack(side="right", fill="both", expand=True)
        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(fill="x", padx=26, pady=(24, 8))
        ctk.CTkLabel(
            header, text="Student Dashboard", font=("Segoe UI", 27, "bold")
        ).pack(side="left")
        ctk.CTkLabel(
            header, text="Manage student records in one place",
            text_color="#94A3B8"
        ).pack(side="right", pady=10)

        stats = ctk.CTkFrame(main, fg_color="transparent")
        stats.pack(fill="x", padx=20, pady=8)
        self.total_value = self.stat_card(stats, "Total Students", "#60A5FA")
        self.course_value = self.stat_card(stats, "Courses", "#34D399")
        self.semester_value = self.stat_card(stats, "Semesters", "#C4B5FD")

        panel = ctk.CTkFrame(main, fg_color=self.PANEL, corner_radius=14)
        panel.pack(fill="both", expand=True, padx=26, pady=(8, 18))
        toolbar = ctk.CTkFrame(panel, fg_color="transparent")
        toolbar.pack(fill="x", padx=16, pady=14)
        ctk.CTkLabel(
            toolbar, text="Student Records", font=("Segoe UI", 17, "bold")
        ).pack(side="left")
        self.search_entry = ctk.CTkEntry(
            toolbar, width=290, placeholder_text="Search name, roll no. or course..."
        )
        self.search_entry.pack(side="right")
        self.search_entry.bind("<KeyRelease>", lambda _event: self.search_students())

        table_frame = ctk.CTkFrame(panel, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        columns = ("id", "name", "roll_no", "email", "phone", "course", "semester")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings")
        headings = ("ID", "Student Name", "Roll Number", "Email", "Phone", "Course", "Semester")
        widths = (45, 150, 110, 180, 110, 130, 75)
        for col, heading, width in zip(columns, headings, widths):
            self.table.heading(col, text=heading)
            self.table.column(col, width=width, anchor="center")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview", background=self.CARD, foreground="white",
            fieldbackground=self.CARD, rowheight=32, borderwidth=0
        )
        style.configure(
            "Treeview.Heading", background="#243650", foreground="white",
            font=("Segoe UI", 10, "bold"), relief="flat"
        )
        style.map("Treeview", background=[("selected", self.BLUE)])
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.table.bind("<<TreeviewSelect>>", self.select_student)

        form = ctk.CTkFrame(panel, fg_color=self.CARD, corner_radius=12)
        form.pack(fill="x", padx=12, pady=(0, 12))
        ctk.CTkLabel(
            form, text="Student Information", font=("Segoe UI", 15, "bold")
        ).grid(row=0, column=0, columnspan=6, padx=12, pady=9, sticky="w")

        field_specs = (
            ("name", "Student name"),
            ("roll_no", "Roll number"),
            ("email", "Email address"),
            ("phone", "Phone number"),
            ("course", "Course / Program"),
            ("semester", "Semester (1-12)"),
        )
        for index, (key, placeholder) in enumerate(field_specs):
            entry = ctk.CTkEntry(form, height=35, placeholder_text=placeholder)
            entry.grid(
                row=1 + index // 3, column=(index % 3) * 2, columnspan=2,
                padx=9, pady=5, sticky="ew"
            )
            self.entries[key] = entry
        for column in range(6):
            form.grid_columnconfigure(column, weight=1)

        actions = ctk.CTkFrame(form, fg_color="transparent")
        actions.grid(row=3, column=0, columnspan=6, pady=(7, 13))
        for label, command, color in (
            ("Add Student", self.add_student, self.BLUE),
            ("Update Selected", self.update_student, self.GREEN),
            ("Delete Selected", self.delete_student, self.RED),
            ("Clear Form", self.clear_form, "#475569"),
        ):
            ctk.CTkButton(
                actions, text=label, command=command, fg_color=color, height=34
            ).pack(side="left", padx=5)

    def stat_card(self, parent, title, color):
        card = ctk.CTkFrame(parent, fg_color=self.CARD, corner_radius=12)
        card.pack(side="left", fill="x", expand=True, padx=6)
        ctk.CTkLabel(card, text=title, text_color="#94A3B8").pack(
            anchor="w", padx=15, pady=(11, 2)
        )
        value = ctk.CTkLabel(
            card, text="0", text_color=color, font=("Segoe UI", 25, "bold")
        )
        value.pack(anchor="w", padx=15, pady=(0, 11))
        return value

    def form_data(self):
        data = {key: entry.get().strip() for key, entry in self.entries.items()}
        if not data["name"] or not data["roll_no"]:
            messagebox.showwarning("Validation", "Name and roll number are required.")
            return None
        if data["email"] and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", data["email"]):
            messagebox.showwarning("Validation", "Enter a valid email address.")
            return None
        if data["phone"] and not re.fullmatch(r"[0-9+()\-\s]{7,20}", data["phone"]):
            messagebox.showwarning("Validation", "Enter a valid phone number.")
            return None
        if data["semester"]:
            try:
                data["semester"] = int(data["semester"])
                if not 1 <= data["semester"] <= 12:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Validation", "Semester must be between 1 and 12.")
                return None
        else:
            data["semester"] = None
        return data

    def add_student(self):
        data = self.form_data()
        if data is None:
            return
        try:
            self.db.execute(
                """INSERT INTO students (name, roll_no, email, phone, course, semester)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                tuple(data[key] for key in (
                    "name", "roll_no", "email", "phone", "course", "semester"
                )),
            )
            messagebox.showinfo("Success", "Student added successfully.")
            self.clear_form()
            self.load_students()
        except Error as exc:
            messagebox.showerror("Database Error", str(exc))

    def load_students(self):
        try:
            rows = self.db.fetch("SELECT * FROM students ORDER BY id DESC")
            self.show_rows(rows)
            self.update_stats()
        except Error as exc:
            messagebox.showerror("Database Error", str(exc))

    def show_rows(self, rows):
        self.table.delete(*self.table.get_children())
        for row in rows:
            self.table.insert("", "end", values=(
                row["id"], row["name"], row["roll_no"], row["email"] or "",
                row["phone"] or "", row["course"] or "", row["semester"] or ""
            ))

    def search_students(self):
        term = f"%{self.search_entry.get().strip()}%"
        try:
            rows = self.db.fetch(
                """SELECT * FROM students
                   WHERE name LIKE %s OR roll_no LIKE %s OR course LIKE %s
                   ORDER BY id DESC""",
                (term, term, term),
            )
            self.show_rows(rows)
        except Error as exc:
            messagebox.showerror("Search Error", str(exc))

    def select_student(self, _event=None):
        selected = self.table.selection()
        if not selected:
            return
        values = self.table.item(selected[0], "values")
        self.selected_id = int(values[0])
        for key, value in zip(
            ("name", "roll_no", "email", "phone", "course", "semester"), values[1:]
        ):
            self.entries[key].delete(0, tk.END)
            self.entries[key].insert(0, value)

    def update_student(self):
        if self.selected_id is None:
            messagebox.showwarning("Selection", "Select a student from the table first.")
            return
        data = self.form_data()
        if data is None:
            return
        try:
            self.db.execute(
                """UPDATE students SET name=%s, roll_no=%s, email=%s,
                   phone=%s, course=%s, semester=%s WHERE id=%s""",
                tuple(data[key] for key in (
                    "name", "roll_no", "email", "phone", "course", "semester"
                )) + (self.selected_id,),
            )
            messagebox.showinfo("Success", "Student updated successfully.")
            self.clear_form()
            self.load_students()
        except Error as exc:
            messagebox.showerror("Update Error", str(exc))

    def delete_student(self):
        if self.selected_id is None:
            messagebox.showwarning("Selection", "Select a student first.")
            return
        if not messagebox.askyesno(
            "Confirm Delete", "Permanently delete this student?"
        ):
            return
        try:
            self.db.execute("DELETE FROM students WHERE id=%s", (self.selected_id,))
            messagebox.showinfo("Deleted", "Student deleted successfully.")
            self.clear_form()
            self.load_students()
        except Error as exc:
            messagebox.showerror("Delete Error", str(exc))

    def clear_form(self):
        self.selected_id = None
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        if hasattr(self, "table"):
            for item in self.table.selection():
                self.table.selection_remove(item)

    def update_stats(self):
        self.total_value.configure(text=str(
            self.db.fetch("SELECT COUNT(*) AS total FROM students")[0]["total"]
        ))
        self.course_value.configure(text=str(
            self.db.fetch(
                "SELECT COUNT(DISTINCT course) AS total FROM students "
                "WHERE course IS NOT NULL AND course <> ''"
            )[0]["total"]
        ))
        self.semester_value.configure(text=str(
            self.db.fetch(
                "SELECT COUNT(DISTINCT semester) AS total FROM students "
                "WHERE semester IS NOT NULL"
            )[0]["total"]
        ))

    def refresh_dashboard(self):
        self.clear_form()
        self.search_entry.delete(0, tk.END)
        self.load_students()

    def close_app(self):
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    app = StudentHub()
    if app.winfo_exists():
        app.mainloop()
