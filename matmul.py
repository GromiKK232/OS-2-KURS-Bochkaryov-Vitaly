import sys
import time
import random
import multiprocessing


def multiply_rows_worker(
    matrix_a, matrix_b, matrix_c,
    rows_a, cols_a, cols_b,
    first_row, last_row,
    completed_rows
):
    """
    Умножает часть строк матрицы A на матрицу B и складывает результат в C.
    """
    for row in range(first_row, last_row):
        # Номер строки C совпадает с номером строки A
        row_start_in_c = row * cols_b

        for t in range(cols_a):
            a_value = matrix_a[row * cols_a + t]

            # Если элемент A нулевой - вся эта итерация ничего не добавит, пропускаем
            if a_value == 0:
                continue

            # Строка t матрицы B начинается с индекса t * cols_b
            row_start_in_b = t * cols_b

            # C[row][j] += A[row][t] * B[t][j]
            for j in range(cols_b):
                matrix_c[row_start_in_c + j] += a_value * matrix_b[row_start_in_b + j]

        # Обновляем счетчик,т.к. одна строка результата готова
        with completed_rows.get_lock():
            completed_rows.value += 1


def print_progress(completed_rows, total_rows):
    last_printed_percent = -67

    while True:
        done = completed_rows.value
        percent = int((done / total_rows) * 100)

        if percent != last_printed_percent:
            print(f"Прогресс: {percent}%", flush=True)
            last_printed_percent = percent

        if done >= total_rows:
            break

        time.sleep(0.2)


def multiply_matrices_parallel(rows_a, cols_a, cols_b, process_count,
                               input_a=None, input_b=None):
    """
    Параллельно умножает матрицы A (rows_a × cols_a) и B (cols_a × cols_b)
    Возвращает:
        elapsed_time — время вычислений в секундах
        checksum — сумма всех элементов результата C
        result_list — матрица C в виде обычного списка
    """
    shared_a = multiprocessing.Array('d', rows_a * cols_a, lock=False)
    shared_b = multiprocessing.Array('d', cols_a * cols_b, lock=False)
    shared_c = multiprocessing.Array('d', rows_a * cols_b, lock=False)

    if input_a is None:
        for i in range(rows_a * cols_a):
            shared_a[i] = random.randint(0, 9)
    else:
        shared_a[:] = input_a

    if input_b is None:
        for i in range(cols_a * cols_b):
            shared_b[i] = random.randint(0, 9)
    else:
        shared_b[:] = input_b

    completed_rows = multiprocessing.Value('i', 0)

    # Делим строки A между процессами:
    # base_rows строк достаётся каждому, а remainder процессов получают на 1 строку больше
    base_rows = rows_a // process_count
    remainder = rows_a % process_count

    workers = []
    current_first_row = 0

    start_time = time.perf_counter()

    progress_process = multiprocessing.Process(
        target=print_progress,
        args=(completed_rows, rows_a)
    )
    progress_process.start()

    for process_index in range(process_count):
        rows_for_this_process = base_rows + (1 if process_index < remainder else 0)

        # Если строк на всех не хватило - этот процесс не нужен
        if rows_for_this_process == 0:
            continue

        current_last_row = current_first_row + rows_for_this_process

        worker = multiprocessing.Process(
            target=multiply_rows_worker,
            args=(
                shared_a, shared_b, shared_c,
                rows_a, cols_a, cols_b,
                current_first_row, current_last_row,
                completed_rows
            )
        )
        workers.append(worker)
        worker.start()

        current_first_row = current_last_row

    # Сначала завершение всех вычислительных процессов, потом - процесса прогресса
    for worker in workers:
        worker.join()

    progress_process.join()

    elapsed_time = time.perf_counter() - start_time

    checksum = sum(shared_c)

    return elapsed_time, checksum, list(shared_c)


if __name__ == "__main__":
    if len(sys.argv) == 5:
        rows_a, cols_a, cols_b, process_count = map(int, sys.argv[1:])
    else:
        rows_a = int(input("Введите количество строк матрицы A (N): "))
        cols_a = int(input("Введите количество столбцов A / строк B (M): "))
        cols_b = int(input("Введите количество столбцов матрицы B (K): "))
        process_count = int(input("Введите количество процессов (T): "))

    if process_count < 1:
        print("Количество процессов должно быть >= 1")
        sys.exit(1)

    print(f"\nЗапуск вычислений для матриц {rows_a}x{cols_a} и {cols_a}x{cols_b} "
          f"на {process_count} процессах...")

    elapsed_time, checksum, _ = multiply_matrices_parallel(
        rows_a, cols_a, cols_b, process_count
    )

    print("\n Результаты ")
    print(f"Время умножения: {elapsed_time:.4f} сек. на {process_count} процессах")
    print(f"Контрольная сумма: {checksum}")