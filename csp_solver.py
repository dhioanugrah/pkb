from constraint import Problem

def add_ppssmmx_constraint(problem, employees, shifts):
    # Menambahkan pola PPXSS (pagi, pagi, libur, malam, malam)
    shift_pattern = ["morning", "morning", "night", "night", "Off"]

    # Setiap karyawan harus mengikuti pola ini
    for employee in employees:
        for i, day in enumerate(shifts.keys()):
            if i < len(shift_pattern):
                problem.addConstraint(
                    lambda current_shift, expected_shift=shift_pattern[i]: current_shift == expected_shift,
                    (day, employee)  # Tidak dalam list
                )

def add_hard_constraints(problem, employees, fields, shifts):
    # Semua karyawan maksimal 1 orang libur di akhir pekan (Sabtu dan Minggu)
    for day in ["Saturday", "Sunday"]:
        problem.addConstraint(
            lambda *shifts: sum(1 for shift in shifts if shift == "Off") == 1,
            [ (day, emp) for emp in employees ]  # Semua karyawan dari semua bidang
        )

    # Bar dan kitchen maksimal 2 orang per shift
    for day in shifts.keys():
        problem.addConstraint(
            lambda *shifts: sum(1 for s in shifts if s != "Off") <= 2,
            [(day, emp) for emp in fields[field]]
        )


    # Bar tidak boleh ada 2 orang pada shift pagi
    for day in shifts.keys():
        problem.addConstraint(
            lambda *shifts: sum(1 for s in shifts if s == "morning" and s == "bar") <= 1,
            [(day, emp) for emp in fields["bar"]]  # Pastikan ini adalah pasangan (day, emp)
        )

    # Waiters: Jika salah satu libur, maka yang lainnya harus shift sore
    for day in shifts.keys():
        problem.addConstraint(
            lambda *shifts: sum(1 for s in shifts if s == "morning" and s == "waiters") == 0,
            [(day, emp) for emp in fields["waiters"] if "Off" in shifts]  # Pastikan ini adalah pasangan (day, emp)
        )

    # Menambahkan pola PPXSS
    add_ppssmmx_constraint(problem, employees, shifts)

def add_soft_constraints(problem, employees, fields, shifts):
    # Setelah shift malam, besoknya tidak shift pagi (opsional)
    # for day, next_day in zip(list(shifts.keys())[:-1], list(shifts.keys())[1:]):
    #     for employee in employees:
    #         problem.addConstraint(
    #             lambda current_shift, next_shift: not (
    #                 current_shift == "night" and next_shift == "morning"
    #             ),
    #             [(day, employee), (next_day, employee)],
    #         )

    # Kitchen: Jika satu libur, shift pagi diusahakan 2 orang
    for day in shifts.keys():
        if "morning" in shifts[day]:
            problem.addConstraint(
                lambda *shifts: sum(1 for s in shifts if s != "Off") >= 2,
                [(day, emp) for emp in fields["kitchen"]]  # Pastikan ini adalah pasangan (day, emp)
            )

def solve_schedule(employees, fields, shifts):
    problem = Problem()

    # Tambahkan variabel CSP
    for day in shifts.keys():
        for employee in employees:
            problem.addVariable((day, employee), shifts[day] + ["Off"])

    # Tambahkan constraints
    add_hard_constraints(problem, employees, fields, shifts)
    add_soft_constraints(problem, employees, fields, shifts)

    # Coba mendapatkan solusi
    solution = problem.getSolution()
    return solution
