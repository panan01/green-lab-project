
# Green Lab Project -- Group 6

## Prerequisites

* Python 3.11.13 or higher
* Ubuntu 20.04 or higher

## Installation & Setup

1.  **Clone the repository**
    ```sh
    git clone git@github.com:panan01/green-lab-project.git
    cd green-lab-project
    ```

2.  **Create and activate a virtual environment (Recommended)**
    Using a virtual environment avoids package version conflicts.
     ```sh
     python3 -m venv venv
     source venv/bin/activate
     ```

3.  **Install dependencies**
    ```sh
    pip install -r requirements.txt
    ```

## How to Run

After installing the dependencies, run the following command from the project's root directory to start an experiment:

```sh
python experiment-runner benchmarks/RunnerConfig.py
```

# Benchmark Suite Status

This document summarizes the current status of the benchmark suite, dividing the benchmarks into two main categories based on the complexity of their optimization paths.

### File Naming Convention

* `_baseline.py`: The original, unoptimized benchmark code.
* `_opt.py`: The final, fully optimized version of the code.
* `_gX.py`: An intermediate version where a specific optimization algorithm `gX` has been applied.

---

## 1. Algorithm Series

The `Algorithm` series benchmarks have multiple viable optimization strategies. Therefore, in addition to the `baseline` and `opt` versions, they include one or more intermediate `gX` versions for testing and comparing different optimization algorithms.

* **`audio_filters`**
    * `_baseline`, `_g1`, `_g3`, `_g6`, `_g7`, `_g8`, `_g9`, `_opt`
* **`basic_string`**
    * `_baseline`, `_g1`, `_g2`, `_g7`, `_g8`, `_opt`
* **`diophantine_equation`**
    * `_baseline`, `_g1`, `_g6`, `_g9`, `_opt`
* **`geometry`**
    * `_baseline`, `_g1`, `_g6`, `_g7`, `_g9`, `_opt`
* **`jacobi_iteration_method`**
    * `_baseline`, `_g1`, `_g3`, `_g5`, `_g6`, `_opt`
* **`lu_decomposition`**
    * `_baseline`, `_g5`, `_g6`, `_g7`, `_g9`, `_opt`
* **`md5`**
    * `_baseline`, `_g1`, `_g3`, `_g6`, `_g7`, `_g9`, `_opt`
* **`merge_sort`**
    * `_baseline`, `_g1`, `_g2`, `_g3`, `_opt`

---

## 2. Trivial Case Series

The `Trivial Case` series benchmarks have only one clear and direct optimization method. Therefore, they only contain a `_baseline.py` (original) and an `_opt.py` (optimized) file, with no intermediate `gX` states.

* **`approx`**: `_baseline`, `_opt`
* **`fib`**: `_baseline`, `_opt`
* **`inline`**: `_baseline`, `_opt`
* **`logic`**: `_baseline`, `_opt`
* **`sort`**: `_baseline`, `_opt`
* **`string_concat`**: `_baseline`, `_opt`
* **`sum_squares`**: `_baseline`, `_opt`
* **`temp_storage`**: `_baseline`, `_opt`
