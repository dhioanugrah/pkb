from constraint import Problem

# Define weekend days
weekend_days = ["Saturday", "Sunday"]

# Function to add a specific scheduling pattern constraint
def add_shift_pattern_constraint(problem, employees, shifts):
    pass  # Disable pattern constraint for now due to strict constraints

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