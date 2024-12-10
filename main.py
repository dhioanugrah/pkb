from constraint import Problem
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox

# --- Helper Functions ---
def is_weekend(day):
    weekday = datetime.strptime(day, "%Y-%m-%d").weekday()
    return weekday >= 5  # Saturday (5) or Sunday (6)

# --- Constraint Functions ---
def add_hard_constraints(problem, employees, fields, shifts):
    for day in shifts.keys():
        # Ensure no more than 1 person is off per field
        for field, field_employees in fields.items():
            problem.addConstraint(
                lambda *shifts: sum(1 for shift in shifts if shift == "Off") <= 1,
                [(day, emp) for emp in field_employees]
            )

        # Max 2 people in Bar or Kitchen per shift
        for field in ["bar", "kitchen"]:
            if field in fields:
                problem.addConstraint(
                    lambda *shifts: sum(1 for shift in shifts if shift != "Off") <= 2,
                    [(day, emp) for emp in fields[field]]
                )

        # Bar-specific constraints
        if "bar" in fields:
            problem.addConstraint(
                lambda *shifts: sum(1 for shift in shifts if shift == "morning") <= 1,
                [(day, emp) for emp in fields["bar"]]
            )

        # Waiter-specific constraints
        if "waiters" in fields:
            problem.addConstraint(
                lambda *shifts: sum(1 for shift in shifts if shift == "night") >= 1,
                [(day, emp) for emp in fields["waiters"]]
            )

# Soft constraints for reducing morning shifts after night shifts
def add_soft_constraints(problem, employees, shifts):
    days = list(shifts.keys())
    for i in range(len(days) - 1):
        for employee in employees:
            problem.addConstraint(
                lambda curr, next_: curr != "night" or next_ != "morning",
                [(days[i], employee), (days[i + 1], employee)]
            )

# --- Scheduling Function ---
def solve_schedule(employees, fields, shifts):
    problem = Problem()

    # Add variables for each day and employee
    for day in shifts.keys():
        for employee in employees:
            problem.addVariable((day, employee), shifts[day] + ["Off"])

    # Add constraints
    add_hard_constraints(problem, employees, fields, shifts)
    add_soft_constraints(problem, employees, shifts)

    # Solve the problem
    solution = problem.getSolution()
    return solution

# --- GUI Functions ---
def add_entry():
    employee = employee_entry.get()
    field = field_combobox.get()

    if not employee or not field:
        messagebox.showerror("Error", "Please fill both Employee and Field.")
        return

    if field not in ["bar", "kitchen", "waiters"]:
        messagebox.showerror("Error", "Invalid field! Use 'bar', 'kitchen', or 'waiters'.")
        return

    employee_field_table.insert("", "end", values=(employee, field))
    employee_entry.delete(0, tk.END)
    field_combobox.set('')

def remove_entry():
    selected_item = employee_field_table.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select an entry to delete.")
        return
    employee_field_table.delete(selected_item)

def generate_schedule():
    employees = []
    fields = {}

    # Collect data from the temporary table
    for row in employee_field_table.get_children():
        employee, field = employee_field_table.item(row)["values"]
        if employee not in employees:
            employees.append(employee)
        if field not in fields:
            fields[field] = []
        fields[field].append(employee)

    # Default shifts setup for 30 days
    start_date = datetime(2024, 1, 1)
    shifts = {start_date + timedelta(days=i): ["morning", "night"] for i in range(30)}

    # Solve the schedule
    solution = solve_schedule(employees, fields, shifts)

    if solution is None:
        messagebox.showerror("Error", "No solution found! Please adjust the constraints.")
    else:
        display_schedule(solution, fields, shifts)

def display_schedule(solution, fields, shifts):
    schedule_table.delete(*schedule_table.get_children())

    for (day_employee, shift) in solution.items():
        day, employee = day_employee
        day_name = datetime.strptime(day, "%Y-%m-%d").strftime("%A")
        field = next((f for f, employees in fields.items() if employee in employees), "Unknown")
        schedule_table.insert("", "end", values=(day, day_name, employee, field, shift))

# --- GUI Setup ---
root = tk.Tk()
root.title("Employee Schedule Generator")

# Input Frame
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

tk.Label(input_frame, text="Employee:").grid(row=0, column=0, sticky="w")
employee_entry = tk.Entry(input_frame, width=30)
employee_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Field:").grid(row=1, column=0, sticky="w")
field_combobox = ttk.Combobox(input_frame, values=["bar", "kitchen", "waiters"], width=28)
field_combobox.grid(row=1, column=1, padx=5, pady=5)

tk.Button(input_frame, text="Add Entry", command=add_entry).grid(row=2, column=0, padx=5, pady=10)
tk.Button(input_frame, text="Remove Entry", command=remove_entry).grid(row=2, column=1, padx=5, pady=10)

# Temporary Table
employee_field_frame = tk.Frame(root)
employee_field_frame.pack(pady=10)

employee_field_table = ttk.Treeview(employee_field_frame, columns=("Employee", "Field"), show="headings")
employee_field_table.heading("Employee", text="Employee")
employee_field_table.heading("Field", text="Field")
employee_field_table.pack(side="left")

scrollbar = ttk.Scrollbar(employee_field_frame, orient="vertical", command=employee_field_table.yview)
employee_field_table.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

# Schedule Button
generate_button = tk.Button(root, text="Generate Schedule", command=generate_schedule)
generate_button.pack(pady=10)

# Schedule Table
schedule_frame = tk.Frame(root)
schedule_frame.pack(pady=10)

schedule_table = ttk.Treeview(schedule_frame, columns=("Date", "Day", "Employee", "Field", "Shift"), show="headings")
schedule_table.heading("Date", text="Date")
schedule_table.heading("Day", text="Day")
schedule_table.heading("Employee", text="Employee")
schedule_table.heading("Field", text="Field")
schedule_table.heading("Shift", text="Shift")
schedule_table.pack(side="left")

schedule_scrollbar = ttk.Scrollbar(schedule_frame, orient="vertical", command=schedule_table.yview)
schedule_table.configure(yscrollcommand=schedule_scrollbar.set)
schedule_scrollbar.pack(side="right", fill="y")

# Run GUI
root.mainloop()
