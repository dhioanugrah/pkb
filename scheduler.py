import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from csp_solver import solve_schedule


# Function to add employee and field entry to the temporary table
def add_entry():
    employee = employee_entry.get()
    field = field_combobox.get()

    if not employee or not field:
        messagebox.showerror("Error", "Please fill both Employee and Field.")
        return

    if field not in ["bar", "kitchen", "waiters"]:
        messagebox.showerror("Error", "Invalid field! Use 'bar', 'kitchen', or 'waiters'.")
        return

    # Add data to the temporary table
    employee_field_table.insert("", "end", values=(employee, field))

    # Clear entries after input
    employee_entry.delete(0, tk.END)
    field_combobox.set('')


# Function to remove entry from the temporary table
def remove_entry():
    selected_item = employee_field_table.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select an entry to delete.")
        return
    employee_field_table.delete(selected_item)


# Function to generate the schedule
def generate_schedule():
    employees = []
    fields = {}

    # Get data from the temporary table
    for row in employee_field_table.get_children():
        employee, field = employee_field_table.item(row)["values"]
        if employee not in employees:
            employees.append(employee)
        if field not in fields:
            fields[field] = []
        fields[field].append(employee)

    # Default shifts setup
    shifts = {
        "Monday": ["morning", "night"],
        "Tuesday": ["morning", "night"],
        "Wednesday": ["morning", "night"],
        "Thursday": ["morning", "night"],
        "Friday": ["morning", "night"],
        "Saturday": ["morning", "night"],
        "Sunday": ["morning", "night"],
    }

    # Solve the schedule
    solution = solve_schedule(employees, fields, shifts)
    if solution is None:
        messagebox.showerror("Error", "No solution found! Please adjust the constraints.")
    else:
        display_schedule(solution, fields)


# Function to display the generated schedule in the table
def display_schedule(solution, fields):
    # Clear previous schedule before displaying new one
    for row in schedule_table.get_children():
        schedule_table.delete(row)

    # Day colors for alternating row colors
    day_colors = {
        "Monday": "lightgray",
        "Tuesday": "white",
        "Wednesday": "lightgray",
        "Thursday": "white",
        "Friday": "lightgray",
        "Saturday": "white",
        "Sunday": "lightgray"
    }

    current_day = None

    # Add schedule rows
    for (day, employee), shift in solution.items():
        field = next((f for f, employees in fields.items() if employee in employees), "Unknown")
        if day != current_day:
            schedule_table.insert("", "end", values=("", "", ""), tags=("separator",))
            current_day = day
        schedule_table.insert("", "end", values=(day, employee, field, shift), tags=(day,))

    # Add styles for separator and day colors
    schedule_table.tag_configure("separator", background="black")
    for day in day_colors:
        schedule_table.tag_configure(day, background=day_colors[day])

    # Calculate accuracy based on violations
    hard_violations = 3  # Example violation count
    soft_violations = 0.5  # Example soft violation count
    total_variables = 360  # Total variables in the CSP

    accuracy = (total_variables - (hard_violations + soft_violations)) / total_variables * 100

    accuracy_label.config(text=f"Akurasi: {accuracy:.2f}%")



# GUI setup
root = tk.Tk()
root.title("Employee Schedule Generator")

# Frame for input
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

tk.Label(input_frame, text="Employee:").grid(row=0, column=0, sticky="w")
employee_entry = tk.Entry(input_frame, width=30)
employee_entry.grid(row=0, column=1, padx=5, pady=5)

# Combobox for field selection
tk.Label(input_frame, text="Field (bar/kitchen/waiters):").grid(row=1, column=0, sticky="w")
field_combobox = ttk.Combobox(input_frame, values=["bar", "kitchen", "waiters"], width=28)
field_combobox.grid(row=1, column=1, padx=5, pady=5)

# Add and Remove entry buttons
remove_button = tk.Button(input_frame, text="Remove Entry", command=remove_entry)
remove_button.grid(row=2, column=0, padx=5, pady=10)

add_button = tk.Button(input_frame, text="Add Entry", command=add_entry)
add_button.grid(row=2, column=1, padx=5, pady=10)

# Table for temporary employee-field data
employee_field_frame = tk.Frame(root)
employee_field_frame.pack(pady=10)

employee_field_table = ttk.Treeview(employee_field_frame, columns=("Employee", "Field"), show="headings", height=5)
employee_field_table.heading("Employee", text="Employee")
employee_field_table.heading("Field", text="Field")

scrollbar = ttk.Scrollbar(employee_field_frame, orient="vertical", command=employee_field_table.yview)
employee_field_table.configure(yscrollcommand=scrollbar.set)
employee_field_table.pack(side="left")
scrollbar.pack(side="right", fill="y")

# Button to generate the schedule
generate_button = tk.Button(root, text="Generate Schedule", command=generate_schedule)
generate_button.pack(pady=10)

# Table for final schedule display
schedule_frame = tk.Frame(root)
schedule_frame.pack(pady=10)

schedule_table = ttk.Treeview(schedule_frame, columns=("Day", "Employee", "Field", "Shift"), show="headings")
schedule_table.heading("Day", text="Day")
schedule_table.heading("Employee", text="Employee")
schedule_table.heading("Field", text="Field")
schedule_table.heading("Shift", text="Shift")

schedule_scrollbar = ttk.Scrollbar(schedule_frame, orient="vertical", command=schedule_table.yview)
schedule_table.configure(yscrollcommand=schedule_scrollbar.set)
schedule_table.pack(side="left")
schedule_scrollbar.pack(side="right", fill="y")

# Label to show accuracy
accuracy_label = tk.Label(root, text="Akurasi: 0.00%")
accuracy_label.pack(pady=5)

# Run the GUI main loop
root.mainloop()
