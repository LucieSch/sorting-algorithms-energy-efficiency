import itertools
import random
import time
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
                tracker = codecarbon.EmissionsTracker()

                ALGORITHMS[algorithm](arr.copy())

                emissions = tracker.stop()
                end = time.perf_counter()
                runtime = end - start

                batch_results.append({
                    "algorithm": algorithm,
                    "dataset": type,
                    "size": size,
                    "batch": batch,
                    "run_in_batch": repeat,
                    "seed": seed,
                    "runtime": runtime,
                    "emissions": emissions
                })
            
            global_run += 1
        
        results.extend(batch_results)

        print(f"===== Finished batch {batch+1}/{NUM_OF_BATCHES}. Waiting for {WAIT_TIME} seconds before next batch... =====")

        # Break between batches to regulate system
        time.sleep(WAIT_TIME)    
    
    df = pd.DataFrame(results)
    df.to_csv(f"{RESULTS_PATH}results.csv", index=False)


def main():
    # print("Starting the sorting algorithms benchmark...")
    # run_experiment()
    # print("Benchmark completed. Results saved to CSV.")
    tracker = codecarbon.EmissionsTracker()
    tracker.start()
    time.sleep(20)
    emissions = tracker.stop()
    print(f"Emissions: {emissions} kg CO2")
   

if __name__ == "__main__":
    main()