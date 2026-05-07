# Energy efficiency of Sorting Algorithms
This project analyzes and compares the runtime and energy efficiency of various sorting algorithms implemented in Python.

The goal is to evaluate not only computational performance but also the energy consumption associated with each algorithm under different input conditions.

## Scope
- Implementation of multiple sorting algorithms (e.g., Bubble Sort, Insertion Sort, Merge Sort, Quick Sort)
- Benchmarking runtime across varying input sizes and distributions
- Estimating energy consumption during execution via CodeCarbon
- Comparing trade-offs between speed and energy efficiency

## Methodology

This project evaluates the runtime and estimmated energy consumption of five sorting algorithms: Bubble Sort, Insertion Sort, Merge Sort, Quick Sort, and Python's built-in sort.

Experiments were conducted using randomly generated integer arrays with sizes of 1,000 and 10,000 elements. Four different input data distributions were considered:
  - Unsorted (random)
  - Already sorted
  - Reverse sorted
  - Nearly sorted

Each algorithm was executed on all dataset types, and both runtime and energy consumption were recorded.

Energy measurements were performed using CodeCarbon. However, due to compatibility issues with macOS and powermetrics, the CPU was not automatically detected. As a workaround, a constant power consumption model of **50 watts** was assumed for all computations.

This means that energy results are directly proportional to runtime and do not reflect real dynamic CPU power behavior.

## Results

<p align="center">
  <img src="results/plots/mean_runtime.png" width="600"><br>
  <em>Runtime Comparison</em>
</p>

<p align="center">
  <img src="results/plots/mean_energy.png" width="600"><br>
  <em>Energy Consumption Comparison</em>
</p>

<p align="center">
  <img src="results/plots/energy_vs_runtime.png" width="600"><br>
  <em>Energy vs Runtime</em>
</p>

Since a constant power model was used, the energy consumption graphs closely mirror the runtime results.

## Limitations
- The energy measurements are based on a **fixed power assumption** (50W) rather than real hardware measurements.
- CodeCarbon could not access CPU-speciifc power metrics due to macOS powermetrics integration issues.
- Energy consumption values are estimates, not precise measurements.
- The model does not account for CPU load variation, frequency scaling, thermal effects or background processes.

Therefore, conclusions about energy efficiency should be interpreted cautiously.

## Key Insights
- Dataset distribution had only a limited impact on runtime and estimated energy consumption, possibly due to the relatively small dataset sizes.
- Unsorted datasets generally caused the highest runtime and energy consumption, while Bubble Sort performed worst on reverse-sorted data.
- Tim Sort was the most efficient algorithm overall, achieving the lowest runtime and estimated energy usage.
- Merge Sort and Quick Sort showed similar performance and energy consumption characteristics.
- Insertion Sort and especially Bubble Sort were significantly less efficient than the other algorithms.
- Overall, the experimental results were largely consistent with the theoretical time complexities of the algorithms.

## Future Work
- Integrate accurate power measurements using supported hardware or external tools.
- Test on different CPUs and operating systems.
- Use larger datasets for scalability analysis.
- Include additional algorithms (e.g., Heap Sort, Selection Sort).
