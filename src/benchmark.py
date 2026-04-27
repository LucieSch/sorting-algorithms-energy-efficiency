import os
os.environ["CODECARBON_NO_POWER_METRICS"] = "1"

import itertools
import random
import time
import logging
from codecarbon import EmissionsTracker
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

WAIT_TIME = 180 # seconds

NUM_OF_BATCHES = 4

REPEATS_PER_BATCH = 10

TOTAL_RUNS = NUM_OF_BATCHES * REPEATS_PER_BATCH

BASE_SEED = 42

DATASET_SIZES = [1000, 10000]

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

                target_time = 2
    
                tracker = EmissionsTracker(
                    output_file=f"emissions_{global_run}.csv",
                    measure_power_secs=1,
                    tracking_mode="process",
                    force_cpu_power=50,
                    log_level="error"
                )
                tracker.start()
                start = time.perf_counter()
                
                runs = 0
                # Run the sorting algorithm multiple times to get a more stable measurement
                while True:
                    ALGORITHMS[algorithm](arr.copy())
                    runs += 1

                    if time.perf_counter() - start >= target_time and runs >= 1:
                        break

                end = time.perf_counter()
                emissions = tracker.stop()
                runtime = end - start
                print(f"Runtime for {algorithm} with {size} elements and {type} dataset: {runtime}, Runs: {runs}")

                # Get energy consumption from code carbon's CSV output
                df = pd.read_csv(f"emissions_{global_run}.csv")
                last_row = df.iloc[-1]

                cpu_energy = last_row["cpu_energy"]
                ram_energy = last_row["ram_energy"]
                energy_consumed = last_row["energy_consumed"]

                batch_results.append({
                    "algorithm": algorithm,
                    "dataset": type,
                    "size": size,
                    "batch": batch,
                    "run_in_batch": repeat,
                    "seed": seed,
                    "runs": runs,
                    "runtime": runtime / runs,
                    "emissions_per_run": emissions / runs,
                    "cpu_energy_per_run": cpu_energy / runs,
                    "ram_energy_per_run": ram_energy / runs,
                    "energy_consumed_per_run": energy_consumed / runs
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