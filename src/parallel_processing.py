import concurrent.futures
import os
import random
import time
from datetime import datetime

import matplotlib.pyplot as plt
import multiprocessing as mp


def time_check(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        return result, execution_time

    return wrapper


def generate_data(size: int) -> list[int]:
    return [random.randint(0, 1000) for _ in range(size)]


def process_number(num: int) -> int:
    result = 1
    for i in range(1, num + 1):
        result *= i

    return result


def worker(in_queue, out_queue):
    while True:
        try:
            idx, num = in_queue.get(timeout=1)
            if num == -1:
                break
            result = process_number(num)
            out_queue.put((idx, result))
        except mp.queues.Empty:
            break


@time_check
def variant_a_thread_pool(data: list[int]) -> list[int]:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = list(executor.map(process_number, data))
    return result


@time_check
def variant_b_process_pool(data: list[int]) -> list[int]:
    num_processes = mp.cpu_count()
    with mp.Pool(num_processes) as pool:
        result = list(pool.map(process_number, data))
    return result


@time_check
def variant_c_process_queue(data: list[int]) -> list[int]:
    num_processes = mp.cpu_count()

    input_queue = mp.Queue()
    output_queue = mp.Queue()

    processes = []
    for _ in range(num_processes):
        p = mp.Process(target=worker, args=(input_queue, output_queue))
        p.start()
        processes.append(p)

    for i, num in enumerate(data):
        input_queue.put((i, num))

    for _ in range(num_processes):
        input_queue.put((-1, -1))

    results = [None] * len(data)
    for _ in range(len(data)):
        index, result = output_queue.get()
        results[index] = result

    for p in processes:
        p.join()

    return results


@time_check
def sequential_processing(data: list[int]) -> list[int]:
    return [process_number(num) for num in data]


def run_benchmark(data_sizes):
    results = {
        "Размер данных": data_sizes,
        "Последовательная обработка": [],
        "ThreadPoolExecutor": [],
        "ProcessPool": [],
        "Process + Queue": [],
    }

    for size in data_sizes:
        print(f"\n--- Тестирование с размером данных: {size} ---")

        data = generate_data(size)

        sequential_result, sequential_time = sequential_processing(data)
        results["Последовательная обработка"].append(sequential_time)

        thread_result, thread_time = variant_a_thread_pool(data)
        results["ThreadPoolExecutor"].append(thread_time)

        process_pool_result, process_pool_time = variant_b_process_pool(data)
        results["ProcessPool"].append(process_pool_time)

        process_queue_result, process_queue_time = variant_c_process_queue(
            data)
        results["Process + Queue"].append(process_queue_time)

    return results


def visualize_results(results):
    data_sizes = results["Размер данных"]

    plt.figure(figsize=(10, 6))

    plt.plot(
        data_sizes,
        results["Последовательная обработка"],
        "o-",
        label="Последовательная обработка",
    )
    plt.plot(
        data_sizes, results["ThreadPoolExecutor"], "s-", label="ThreadPoolExecutor"
    )
    plt.plot(data_sizes, results["ProcessPool"], "^-", label="ProcessPool")
    plt.plot(data_sizes, results["Process + Queue"],
             "D-", label="Process + Queue")

    plt.xlabel("Размер данных")
    plt.ylabel("Время выполнения (секунды)")
    plt.title("Сравнение времени выполнения разных вариантов параллельной обработки")
    plt.grid(True)
    plt.legend()

    plt.tight_layout()

    os.makedirs("results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join("results", f"benchmark_plot_{timestamp}.png")
    plt.savefig(filepath)

    print(f"\nГрафик сохранен в файл: {filepath}")

    plt.show()

    return filepath


def main():
    data_sizes = [1000, 5000, 10000, 20000]

    print(f"Запуск тестирования для размеров данных: {data_sizes}")
    print(f"Количество ядер CPU: {mp.cpu_count()}")

    results = run_benchmark(data_sizes)

    visualize_results(results)


if __name__ == "__main__":
    main()
