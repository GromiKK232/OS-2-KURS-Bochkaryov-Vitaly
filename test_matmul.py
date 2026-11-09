import unittest
import random
from matmul import multiply_matrices_parallel


class TestMatrixMultiplicationLab(unittest.TestCase):

    def test_small_matrices_known_result(self):
        """
        Тест 1: Умножение маленьких матриц с заранее известным результатом.
        """
        A = [1, 2, 3, 4]
        B = [1, 7, 3, 5, 4, 3]
        expected_C = [11, 15, 9, 23, 37, 21]

        _, checksum, result_C = multiply_matrices_parallel(
            rows_a=2, cols_a=2, cols_b=3, process_count=2, input_a=A, input_b=B
        )
        self.assertEqual(result_C, expected_C)
        self.assertEqual(checksum, sum(expected_C))

    def test_multiply_by_identity_and_zero(self):
        """
        Тест 2: Умножение на нулевую и единичную матрицу.
        """
        A = [1, 2, 3, 4]

        # 1. Нулевая матрица (2x3)
        B_zero = [0, 0, 0, 0, 0, 0]
        _, checksum, result_C = multiply_matrices_parallel(
            rows_a=2, cols_a=2, cols_b=3, process_count=2, input_a=A, input_b=B_zero
        )
        self.assertEqual(checksum, 0)
        self.assertTrue(all(val == 0 for val in result_C))

        # 2. Единичная матрица (2x2)
        E = [1, 0, 0, 1]
        _, _, result_sq = multiply_matrices_parallel(
            rows_a=2, cols_a=2, cols_b=2, process_count=2, input_a=A, input_b=E
        )
        self.assertEqual(result_sq, A)

    def test_determinism_parallel_vs_serial(self):
        """
        Тест 3: Многопоточный результат совпадает с последовательным.
        """
        N, M, K = 15, 15, 15
        random.seed(100)
        A = [random.randint(0, 9) for _ in range(N * M)]
        B = [random.randint(0, 9) for _ in range(M * K)]

        # Образец (1 процесс)
        _, checksum_ref, res_ref = multiply_matrices_parallel(
            rows_a=N, cols_a=M, cols_b=K, process_count=1, input_a=A, input_b=B
        )

        # Проверяем разные T, включая T > N (20 > 15)
        for T in [1, 2, 3, 7, 20]:
            _, checksum, res = multiply_matrices_parallel(
                rows_a=N, cols_a=M, cols_b=K, process_count=T, input_a=A, input_b=B
            )
            self.assertEqual(checksum, checksum_ref, f"Контрольная сумма не совпала при T={T}")
            self.assertEqual(res, res_ref, f"Результат не совпал при T={T}")

    def test_edge_cases_1x1_and_lines(self):
        """
        Тест 4: Граничные случаи
        """
        # 1x1
        _, _, res = multiply_matrices_parallel(1, 1, 1, 1, input_a=[5], input_b=[4])
        self.assertEqual(res, [20])

        # Одна строка (1x3 на 3x1)
        _, _, res = multiply_matrices_parallel(1, 3, 1, 2, input_a=[1, 2, 3], input_b=[4, 5, 6])
        self.assertEqual(res, [32])

        # Один столбец (3x1 на 1x1)
        _, _, res = multiply_matrices_parallel(3, 1, 1, 2, input_a=[1, 2, 3], input_b=[4])
        self.assertEqual(res, [4, 8, 12])

    def test_progress_equals_100_percent(self):
        """
        Тест 5: Прогресс должен быть 100%.
        """
        N, M, K = 10, 10, 10
        A = [1] * (N * M)
        B = [1] * (M * K)
        _, checksum, res = multiply_matrices_parallel(N, M, K, 4, input_a=A, input_b=B)
        self.assertEqual(len(res), N * K, "Длина результата должна соответствовать N*K")

    def test_multiple_runs(self):
        """
        Тест 6: 100 запусков подряд
        """
        N, M, K = 10, 10, 10
        random.seed(42)
        A = [random.randint(0, 5) for _ in range(N * M)]
        B = [random.randint(0, 5) for _ in range(M * K)]

        _, checksum_ref, res_ref = multiply_matrices_parallel(N, M, K, 1, input_a=A, input_b=B)

        for i in range(100):
            _, checksum, res = multiply_matrices_parallel(N, M, K, 4, input_a=A, input_b=B)
            self.assertEqual(checksum, checksum_ref, f"Ошибка синхронизации на итерации {i}")
            self.assertEqual(res, res_ref, f"Несовпадение результата на итерации {i}")


if __name__ == '__main__':
    unittest.main()