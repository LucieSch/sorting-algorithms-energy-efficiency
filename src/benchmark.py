import itertools
import random
import time
import logging
import codecarbon
import pandas as pd
from data.generated_inputs import generate_all_int_inputs
from src.sorting_algorithms import bubble_sort, insertion_sort, merge_sort, quick_sort, tim_sort

RESULTS_PATH = "results/raw_data/"

ALGORITHMS = {
    "bubble_sort": bubble_sort,
    "insertion_sort": insertion_sort,
    "merge_sort": merge_sort,
    "quick_sort": quick_sort,
    "tim_sort": tim_sort
}

WAIT_TIME = 1200 # seconds

NUM_OF_BATCHES = 4

REPEATS_PER_BATCH = 10

TOTAL_RUNS = NUM_OF_BATCHES * REPEATS_PER_BATCH

BASE_SEED = 42

DATASET_SIZES = [1000, 10000, 100000]

DATASET_TYPES = ["unsorted", "sorted", "reverse_sorted", "almost_sorted"]

class IgnoreMultipleInstances(logging.Filter):
    def filter(self, record):
        return "Multiple instances of codecarbon" not in record.getMessage()

def get_all_inputs(seed):
    data = {}
    for size in DATASET_SIZES:
        data[size] = generate_all_int_inputs(size, seed=seed)
    
    return data

def run_experiment():
    results = []

    global_run = 0

    for batch in range(NUM_OF_BATCHES):
        print(f"===== Starting batch {batch+1}/{NUM_OF_BATCHES} =====")
        batch_results = []

        for repeat in range(REPEATS_PER_BATCH):
            print(f"    Run {repeat+1}/{REPEATS_PER_BATCH} in batch {batch+1}...")
            seed = BASE_SEED + global_run
            data = get_all_inputs(seed)

            combinations = list(itertools.product(ALGORITHMS.keys(), DATASET_SIZES, DATASET_TYPES))

            # Randomize the order of the algorithms and data for each iteration to avoid bias
            random.shuffle(combinations)

            for algorithm, size, type in combinations:
                arr = data[size][type]

                # Warmup
                ALGORITHMS[algorithm](arr.copy())

                start = time.perf_counter()
                tracker = codecarbon.EmissionsTracker(
                    measure_power_secs=1,
                    tracking_mode="process",
                    force_cpu_power=50,
                    log_level="error"
                )
                tracker.start()

                ALGORITHMS[algorithm](arr.copy())

                emissions = tracker.stop()
                end = time.perf_counter()
                runtime = end - start

                # Get energy consumption from code carbon's CSV output
                df = pd.read_csv("/Users/lucieschwendrat/Projects/git/sorting-algorithms-energy-efficiency/emissions.csv")
                last_row = df.iloc[-1]

                cpu_energy = last_row["cpu_energy"]
                gpu_energy = last_row["gpu_energy"]
                ram_energy = last_row["ram_energy"]
                energy_consumed = last_row["energy_consumed"]

                batch_results.append({
                    "algorithm": algorithm,
                    "dataset": type,
                    "size": size,
                    "batch": batch,
                    "run_in_batch": repeat,
                    "seed": seed,
                    "runtime": runtime,
                    "emissions": emissions,
                    "cpu_energy": cpu_energy,
                    "gpu_energy": gpu_energy,
                    "ram_energy": ram_energy,
                    "energy_consumed": energy_consumed
                })
            
            global_run += 1
        
        results.extend(batch_results)

        print(f"===== Finished batch {batch+1}/{NUM_OF_BATCHES}. Waiting for {WAIT_TIME} seconds before next batch... =====")

        # Break between batches to regulate system
        time.sleep(WAIT_TIME)    
    
    df = pd.DataFrame(results)
    df.to_csv(f"{RESULTS_PATH}results.csv", index=False)


def main():
    print("Starting the sorting algorithms benchmark...")
    logger = logging.getLogger("codecarbon")
    logger.addFilter(IgnoreMultipleInstances())
    
    run_experiment()
    print("Benchmark completed. Results saved to CSV.")
   

if __name__ == "__main__":
    main()