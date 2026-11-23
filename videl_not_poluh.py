import mmap
import time


def print_memory_stats(step_name, prev_page_faults=0, elapsed_ms=0.0):
    with open("/proc/self/status") as status_file:
        memory_kb = {
            file_line.split(":")[0]: int(file_line.split()[1])
            for file_line in status_file
            if file_line.startswith(("VmSize:", "VmRSS:"))
        }

    with open("/proc/self/stat") as stat_file:
        stats_after_name = stat_file.read().rsplit(")", 1)[1]
        current_page_faults = int(stats_after_name.split()[7])

    print(
        f"{step_name:<25} VmSize: {memory_kb['VmSize']/1024:6.1f} МиБ  RSS:"
        f" {memory_kb['VmRSS']/1024:6.1f} МиБ  +minflt: {current_page_faults - prev_page_faults:6} "
        f" {elapsed_ms:6.1f} мс"
    )
    return current_page_faults


page_size = mmap.PAGESIZE
total_bytes = 256 << 20

current_page_faults = print_memory_stats("Начало")
memory_block = mmap.mmap(-1, total_bytes, flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS)
current_page_faults = print_memory_stats("После выделения", current_page_faults)

start_time = time.perf_counter()
bytes_sum = sum(memory_block[byte_offset] for byte_offset in range(0, total_bytes, page_size))
current_page_faults = print_memory_stats("Первое чтение", current_page_faults, (time.perf_counter() - start_time) * 1000)

start_time = time.perf_counter()
for byte_offset in range(0, total_bytes, page_size):
    memory_block[byte_offset] = 1
current_page_faults = print_memory_stats("Первая запись", current_page_faults, (time.perf_counter() - start_time) * 1000)

start_time = time.perf_counter()
for byte_offset in range(0, total_bytes, page_size):
    memory_block[byte_offset] = 2
current_page_faults = print_memory_stats("Повторная запись", current_page_faults, (time.perf_counter() - start_time) * 1000)

assert memory_block[0] == memory_block[page_size] == memory_block[2 * page_size] == memory_block[((total_bytes - 1) // page_size) * page_size] == 2
memory_block.close()
print_memory_stats("После освобождения", current_page_faults)
print("Контрольная сумма:", bytes_sum)
