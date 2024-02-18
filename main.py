from ortools.sat.python import cp_model
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def schedule_tasks(N, P, M, instruments, tasks):
    model = cp_model.CpModel()

    # Variables
    task_starts = {}

    for plate in range(1, P + 1):
        for task_num, (instrument, duration) in enumerate(tasks, start=1):
            task_starts[plate, task_num] = model.NewIntVar(0, cp_model.INT_MAX, f'start_plate{plate}_task{task_num}')

    # Constraints
    for plate in range(1, P + 1):
        for task_num in range(1, M + 1):
            if task_num > 1:
                model.Add(task_starts[plate, task_num] >= task_starts[plate, task_num - 1] + tasks[task_num - 1][1])

            if plate > 1:
                model.Add(task_starts[plate, task_num] >= task_starts[plate - 1, task_num])

    # Objective
    objective = model.NewIntVar(0, cp_model.INT_MAX, 'objective')
    model.AddMaxEquality(objective, [task_starts[P, task_num] + tasks[task_num - 1][1] for task_num in range(1, M + 1)])
    model.Minimize(objective)

    # Solver
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Debug prints
    print(f'Solver status: {solver.StatusName(status)}')
    print(f'Objective value: {solver.ObjectiveValue()}')

    # Retrieve the solution
    completion_times = {}
    if status == cp_model.OPTIMAL:
        for plate in range(1, P + 1):
            for task_num in range(1, M + 1):
                start_time = solver.Value(task_starts[plate, task_num])
                completion_times.setdefault(plate, []).append((start_time, start_time + tasks[task_num-1][1]))

    return completion_times, solver.ObjectiveValue()



def plot_gantt_chart(completion_times, instruments):
    fig, ax = plt.subplots()

    for plate, tasks in completion_times.items():
        for task_num, (start_time, end_time) in enumerate(tasks, start=1):
            instrument = instruments[task_num - 1]
            ax.broken_barh([(start_time, end_time - start_time)], (plate - 1, 1), facecolors='blue', edgecolor='black')
            ax.text(start_time + 0.1, plate - 0.5, f'{instrument} - T{task_num}', color='black', fontsize=8)

    ax.set_ylim(0, len(completion_times))
    ax.set_xlabel('Time')
    ax.set_yticks(range(1, len(completion_times) + 1))
    ax.set_yticklabels([f'Plate {plate}' for plate in completion_times.keys()])
    ax.grid(True)
    ax.xaxis_date()
    # ax.xaxis.set_major_locator(mdates.MaxNLocator(integer=True))
    ax.set_title('Gantt Chart - Plate Journey')

    plt.show()

def plot_instrument_utilization(completion_times, instruments):
    fig, ax = plt.subplots()

    for task_num, instrument in enumerate(instruments, start=1):
        task_times = [(start, end) for tasks in completion_times.values() for start, end in tasks if task_num <= len(tasks)]
        ax.broken_barh(task_times, (task_num - 1, 1), facecolors='green', edgecolor='black')
        ax.text(0.1, task_num - 0.5, f'{instrument} - T{task_num}', color='black', fontsize=8)

    ax.set_ylim(0, len(instruments))
    ax.set_xlabel('Time')
    ax.set_yticks(range(1, len(instruments) + 1))
    ax.set_yticklabels([f'{instrument}' for instrument in instruments])
    ax.grid(True)
    ax.xaxis_date()
    # ax.xaxis.set_major_locator(mdates.DateLocator())
    ax.set_title('Gantt Chart - Instrument Utilization')

    plt.show()

# Example usage
N = 4  # Number of instruments
P = 10  # Number of plates
M = 8  # Number of tasks
instruments = ['rinse', 'wash', 'dry', 'spin']
tasks = [('rinse', 2), ('wash', 3), ('rinse', 2), ('dry', 4), ('spin', 2), ('rinse', 2), ('wash', 3), ('dry', 4)]

completion_times, total_completion_time = schedule_tasks(N, P, M, instruments, tasks)

# Print the result
print("Plate Completion Times:")
for plate, times in completion_times.items():
    print(f"Plate {plate}: {times}")

print("\nTotal Completion Time:", total_completion_time)

# Plot Gantt charts
plot_gantt_chart(completion_times, instruments)
plot_instrument_utilization(completion_times, instruments)
