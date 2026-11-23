import time
import numpy as np

matrix_size = 8192
matrix = np.arange(matrix_size * matrix_size, dtype=np.int32).reshape(matrix_size, matrix_size)

row_times_ms = []
col_times_ms = []

for attempt in range(3):
    start_time = time.perf_counter()
    row_sum = 0
    for row_index in range(matrix_size):
        row_sum += int(matrix[row_index, :].sum())
    row_times_ms.append((time.perf_counter() - start_time) * 1000)

    start_time = time.perf_counter()
    col_sum = 0
    for col_index in range(matrix_size):
        col_sum += int(matrix[:, col_index].sum())
    col_times_ms.append((time.perf_counter() - start_time) * 1000)

    assert row_sum == col_sum
    print(f"Замер {attempt}: строки = {row_times_ms[-1]:.2f} мс | столбцы = {col_times_ms[-1]:.2f} мс | сумма = {row_sum}")

avg_row_ms = sum(row_times_ms) / 3
avg_col_ms = sum(col_times_ms) / 3
print(f"\nСреднее по строкам: {avg_row_ms:.2f} мс")
print(f"Среднее по столбцам: {avg_col_ms:.2f} мс")
print(f"Медленнее в: {avg_col_ms / avg_row_ms:.2f} раз(а)")
