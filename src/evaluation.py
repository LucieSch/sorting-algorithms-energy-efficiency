import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

RESULTS_PATH = "results/raw_data/results.csv"

ALGORITHMS = ["bubble_sort", "insertion_sort", "merge_sort", "quick_sort", "tim_sort"]

ALGORITHM_NAMES = {
    "bubble_sort": "Bubble Sort",
    "insertion_sort": "Insertion Sort",
    "merge_sort": "Merge Sort",
    "quick_sort": "Quick Sort",
    "tim_sort": "Tim Sort"
}

DATASET_SIZES = [1000, 10000]

DATASET_TYPES = ["unsorted", "sorted", "reverse_sorted", "almost_sorted"]

ALGORITHM_COLORS = {
    "bubble_sort": "#ffbc42",
    "insertion_sort": "#d81159",
    "merge_sort": "#8f2d56",
    "quick_sort": "#218380",
    "tim_sort": "#73d2de"
}

ALGORITHMS_MARKERS = {
    "bubble_sort": "o",
    "insertion_sort": "s",
    "merge_sort": "^",
    "quick_sort": "D",
    "tim_sort": "X"
}

def prepare_data():
    df = pd.read_csv(RESULTS_PATH)

    # Convert from kWH to Ws
    df["energy_consumed_per_run"] *= 3600000
    df["cpu_energy_per_run"] *= 3600000
    df["ram_energy_per_run"] *= 3600000

    summary = df.groupby(["algorithm", "size", "dataset"]).agg(
        mean_energy=("energy_consumed_per_run", "mean"),
        std_energy=("energy_consumed_per_run", "std"),
        mean_runtime=("runtime", "mean"),
        std_runtime=("runtime", "std"),
        count=("energy_consumed_per_run", "count")
    )

    summary["cv_energy"] = summary["std_energy"] / summary["mean_energy"]
    summary["cv_runtime"] = summary["std_runtime"] / summary["mean_runtime"]
    summary["upper_bound_energy"] = summary["mean_energy"] + summary["std_energy"]
    summary["lower_bound_energy"] = summary["mean_energy"] - summary["std_energy"]
    summary["upper_bound_runtime"] = summary["mean_runtime"] + summary["std_runtime"]
    summary["lower_bound_runtime"] = summary["mean_runtime"] - summary["std_runtime"]

    summary.sort_values("cv_energy", ascending=False)
    summary.to_csv("results/raw_data/summary.csv")

    return summary

def plot_results(summary, col_mean, col_std, ylabel, title):
    for size in DATASET_SIZES:
        fig, ax = plt.subplots(figsize=(12, 6))

        x = np.arange(len(ALGORITHMS))
        width = 0.225

        mean_y1 = [summary.loc[(alg, size, "unsorted"), col_mean] for alg in ALGORITHMS]
        mean_y2 = [summary.loc[(alg, size, "sorted"), col_mean] for alg in ALGORITHMS]
        mean_y3 = [summary.loc[(alg, size, "reverse_sorted"), col_mean] for alg in ALGORITHMS]
        mean_y4 = [summary.loc[(alg, size, "almost_sorted"), col_mean] for alg in ALGORITHMS]

        std_y1 = [summary.loc[(alg, size, "unsorted"), col_std] for alg in ALGORITHMS]
        std_y2 = [summary.loc[(alg, size, "sorted"), col_std] for alg in ALGORITHMS]
        std_y3 = [summary.loc[(alg, size, "reverse_sorted"), col_std] for alg in ALGORITHMS]
        std_y4 = [summary.loc[(alg, size, "almost_sorted"), col_std] for alg in ALGORITHMS]

        bars1 = ax.bar( x - 1.5 * width, mean_y1, yerr=std_y1, capsize=5, width=width, label="Unsorted", color="#6C3428", linewidth=0.6)
        bars2 = ax.bar(x - 0.5 * width, mean_y2, yerr=std_y2, capsize=5, width=width, label="Sorted", color="#BA704F", linewidth=0.6)
        bars3 = ax.bar(x + 0.5 * width, mean_y3, yerr=std_y3, capsize=5, width=width, label="Reverse Sorted", color="#DFA878", linewidth=0.6)
        bars4 = ax.bar(x + 1.5 * width, mean_y4, yerr=std_y4, capsize=5, width=width, label="Almost Sorted", color="#CEE6F3", linewidth=0.6)

        # Logarithmic y-axis
        ax.set_yscale("log")

        for bars in [bars1, bars2, bars3, bars4]:
            ax.bar_label(bars, fmt="%.4f", padding=3, fontsize=7)

        ax.set_xticks(x)
        ax.set_xticklabels([ALGORITHM_NAMES[a] for a in ALGORITHMS])
        ax.set_xlabel("Sorting Algorithm")
        ax.set_ylabel(ylabel)
        fig.suptitle(f"{title} for Dataset Size {size}", fontsize=14, y=0.98)
        fig.legend(title="Dataset Type", loc="upper center", ncol=4, bbox_to_anchor=(0.5, 0.94), frameon=False)

        fig.tight_layout(rect=[0, 0, 1, 0.92])
        fig.savefig(f"results/plots/{col_mean}_{size}.png", dpi=300, bbox_inches="tight")

        plt.close(fig)

def plot_energy_vs_runtime():
    df = pd.read_csv(RESULTS_PATH)

    df["energy_consumed_per_run"] *= 3600000
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), sharey=True, sharex=True)
    fig.suptitle("Energy Consumption vs Runtime", fontsize=14, y=0.98)

    for algorithm in ALGORITHMS:
        subset_1000 = df[(df["algorithm"] == algorithm) & (df["size"] == 1000)]
        subset_10000 = df[(df["algorithm"] == algorithm) & (df["size"] == 10000)]

        colors = [ALGORITHM_COLORS[algorithm] for _ in range(len(subset_1000))]

        ax1.scatter(
            subset_1000["runtime"],
            subset_1000["energy_consumed_per_run"],
            label=ALGORITHM_NAMES[algorithm],
            color=colors,
            marker=ALGORITHMS_MARKERS[algorithm],
            alpha=0.5,
            s=100,
            edgecolor="none"
        )

        ax2.scatter(
            subset_10000["runtime"],
            subset_10000["energy_consumed_per_run"],
            label=ALGORITHM_NAMES[algorithm],
            color=colors,
            marker=ALGORITHMS_MARKERS[algorithm],
            alpha=0.5,
            s=100,
            edgecolor="none"
        )

    for ax in [ax1, ax2]:
        ax.set_xscale("log")
        ax.set_yscale("log")

        ax.set_xlabel("Runtime [s]")

    ax1.set_ylabel("Energy Consumption [Ws]")

    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, title="Sorting Algorithm", loc="upper center", ncol=5, bbox_to_anchor=(0.5, 0.94), frameon=False)
    ax1.set_title("Dataset Size 1000")
    ax2.set_title("Dataset Size 10000")

    plt.tight_layout(rect=[0, 0, 1, 0.9])
    fig.savefig("results/plots/energy_vs_runtime.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def evaluate_results():
    summary = prepare_data()

    plot_results(summary, "mean_energy", "std_energy", "Energy Consumption [Ws]", "Mean Energy Consumption of Sorting Algorithms")
    plot_results(summary, "mean_runtime", "std_runtime", "Runtime [s]", "Mean Runtime of Sorting Algorithms")

    plot_energy_vs_runtime()


def main():
    print("Evaluating results...")
    evaluate_results()

if __name__ == "__main__":
    main()