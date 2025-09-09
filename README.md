# Empirical assessment of guidelines to write energy-efficient Python code.

Overleaf Project Link: https://www.overleaf.com/project/68bea01af5298d89cdee7e7a

### 优化案例
好的，我们来以这个 `float.py` 基准测试为例，具体说明你需要做什么。

### 1. 理解 `float.py` 基准测试

这个 `float.py` 文件是一个浮点数密集型基准测试，它主要做了以下几件事：

*   **定义 `Point` 类：** 一个包含 `x`, `y`, `z` 三个浮点数坐标的类。使用了 `__slots__` 来优化内存使用（减少字典开销）。
    *   `__init__`：根据一个索引 `i` 计算 `x`, `y`, `z` 的初始值，涉及 `sin`, `cos` 等三角函数。
    *   `normalize`：将点的向量归一化，使其长度（模）为1。这涉及平方、求和、开方和除法等大量浮点运算。
    *   `maximize`：将当前点与另一个点进行比较，将每个坐标（x, y, z）更新为两者中的最大值。
*   **`maximize(points)` 函数：** 遍历一个点列表，将列表中的所有点依次与前一个最大点进行比较，最终返回一个所有坐标都是最大值的点。
*   **`benchmark(n)` 函数：** 这是 `pyperformance` 实际测试的主要逻辑。
    1.  创建一个包含 `n` 个 `Point` 对象的列表。
    2.  遍历所有点，调用它们的 `normalize()` 方法。
    3.  调用全局的 `maximize(points)` 函数。
*   **`pyperf.Runner` 部分：** 这是 `pyperformance` 框架用来运行 `benchmark` 函数并测量其执行时间的部分。它会多次运行 `benchmark` 函数（参数为 `POINTS=100000`），然后进行统计。

### 2. 你的任务分解与示例操作

你的任务是选择一些能效指导原则，并尝试将它们应用于 `float.py` 中的代码，创建优化版本，然后比较性能。

**步骤概述：**

1.  **复制文件，准备基准：** 将 `float.py` 复制到你的工作目录，并将其命名为 `float_original.py`。这是你的“未优化”版本。
2.  **选择指导原则，并创建优化版本：** 再次复制 `float_original.py`，命名为 `float_optimized_gX.py` (其中 `gX` 代表你应用的指导原则)。然后根据选定的指导原则修改这个文件。
3.  **功能验证：** 编写一个小的测试脚本，确保 `float_original.py` 和 `float_optimized_gX.py` 在给定相同输入时，产生相同的结果。
4.  **运行基准测试并收集数据：** 使用 `pyperf.Runner` 运行两个版本，并额外使用系统工具收集能耗、CPU和内存数据。
5.  **分析和报告。**

**示例：应用“代码优化”家族中的 G5 (使用内建/库函数)**

我们来选择一个相对简单的优化点：`Point.maximize` 方法。

**原始 `Point.maximize` 方法：**
```python
    def maximize(self, other):
        self.x = self.x if self.x > other.x else other.x
        self.y = self.y if self.y > other.y else other.y
        self.z = self.z if self.z > other.z else other.z
        return self
```
这里使用了条件表达式来取两个数中的最大值。Python有一个内建函数 `max()` 可以做同样的事情，通常内建函数会比纯Python实现的逻辑更快。

**2.1. 复制文件并创建优化版本**

*   **原始文件：**
    将 `float.py` 复制到你的项目目录，命名为 `float_original.py`。

*   **优化文件：**
    将 `float_original.py` 再次复制一份，命名为 `float_optimized_g5.py`。
    现在，打开 `float_optimized_g5.py` 进行修改。

**2.2. 应用指导原则 (G5)**

修改 `float_optimized_g5.py` 中的 `Point.maximize` 方法：

```python
# float_optimized_g5.py
# ... (其他代码保持不变) ...

class Point(object):
    __slots__ = ('x', 'y', 'z')

    # ... (__init__, __repr__, normalize 保持不变) ...

    def maximize(self, other):
        # 应用 G5: 使用内置的 max() 函数
        self.x = max(self.x, other.x)
        self.y = max(self.y, other.y)
        self.z = max(self.z, other.z)
        return self

# ... (maximze(points), benchmark, if __name__ == "__main__": 部分保持不变) ...
```
**注意：** 为了在 `pyperf.Runner` 中区分不同的基准，你可以修改 `benchmark` 函数的名称，或者在 `runner.bench_func` 中给它一个不同的标签。这里为了简化，我们暂时保留 `benchmark` 函数名，但会在 `runner.bench_func` 中给它不同的标签。

### 3. 功能验证

在你测量性能之前，**必须**确保优化后的代码功能完全正确，与原始代码产生相同的结果。

创建一个 `verify_float.py` 文件：

```python
# verify_float.py
from float_original import benchmark as original_benchmark, Point as OriginalPoint, POINTS
from float_optimized_g5 import benchmark as optimized_benchmark, Point as OptimizedPoint # 导入优化版本

def run_and_compare(func_original, func_optimized, n_points):
    print(f"Testing with {n_points} points...")

    # 运行原始版本
    original_result = func_original(n_points)
    print(f"Original result: {original_result}")

    # 运行优化版本
    optimized_result = func_optimized(n_points)
    print(f"Optimized result: {optimized_result}")

    # 比较结果
    # 由于浮点数精度问题，直接 == 比较可能不准确，最好比较接近程度
    # 但对于这个简单的 max 优化，通常会是完全一致的
    if (abs(original_result.x - optimized_result.x) < 1e-9 and
        abs(original_result.y - optimized_result.y) < 1e-9 and
        abs(original_result.z - optimized_result.z) < 1e-9):
        print("Functionality check: PASS! Results are identical (within tolerance).")
    else:
        print("Functionality check: FAIL! Results differ.")

if __name__ == "__main__":
    # 使用较小的点数进行快速验证
    run_and_compare(original_benchmark, optimized_benchmark, 100)
    # 也可以使用 POINTS 进行完整验证
    run_and_compare(original_benchmark, optimized_benchmark, POINTS)
```
运行 `python verify_float.py`。如果输出 `PASS`，则表示功能一致性验证通过。

### 4. 运行基准测试并收集数据

你需要一个主脚本来运行这两个版本的基准测试，并收集你需要的指标。

创建一个 `run_benchmarks.py` 文件：

```python
# run_benchmarks.py
import pyperf
import os
import sys

# 假设 float_original.py 和 float_optimized_g5.py 在同一个目录下
# 需要确保这两个文件有各自独立的 __name__ == "__main__": 块
# 但由于 pyperf.Runner 会导入并调用 bench_func，所以保持它们的 if __name__ == "__main__": 块不变即可

if __name__ == "__main__":
    runner = pyperf.Runner()
    runner.metadata['description'] = "Float Benchmark with G5 Optimization Comparison"

    # 设置点数
    n_points = 100000 # 使用与 float.py 中相同的 POINTS 值

    print("\n--- Running Original Benchmark ---")
    # 导入原始基准函数，并为其指定一个名称 'float_original'
    from float_original import benchmark as original_float_benchmark
    runner.bench_func('float_original', original_float_benchmark, n_points)

    print("\n--- Running Optimized G5 Benchmark ---")
    # 导入优化后的基准函数，并为其指定一个名称 'float_optimized_g5'
    from float_optimized_g5 import benchmark as optimized_g5_float_benchmark
    runner.bench_func('float_optimized_g5', optimized_g5_float_benchmark, n_points)

    print("\nBenchmark runs completed. Results in .json files.")

    # --- 额外的指标收集说明 ---
    print("\n--- Collecting Other Metrics (Manual/External Tools) ---")
    print("For Energy Usage, CPU Usage, and Memory Usage, you will need to run these benchmarks ")
    print("with external profiling tools (e.g., powerstat, perf, memory_profiler, top/htop).")
    print("Example for CPU/Memory (Linux, in a separate terminal while benchmarks run): `top -p <python_process_id>`")
    print("Example for Memory (using memory_profiler, requires modifying the benchmark functions to be decorated):")
    print("  `pip install memory_profiler`")
    print("  Then run: `python -m memory_profiler run_benchmarks.py` (or individual benchmark files)")

    # 简单的运行原始和优化版本，用于手动观察其他指标
    # 注意：这些不通过 pyperf.Runner 运行的计时可能不如 pyperf 准确
    # 但可以用于配合外部工具进行手动测量
    print("\n--- Manual run for external metric collection (e.g., top, powerstat) ---")
    print("You might want to run these commands in separate terminal sessions:")
    print(f"python -c 'from float_original import benchmark; benchmark({n_points})'")
    print(f"python -c 'from float_optimized_g5 import benchmark; benchmark({n_points})'")
    print("While these commands are running, use your system's profiling tools.")

```

**运行 `python run_benchmarks.py`。**

`pyperf.Runner` 会为你运行这两个基准测试，并生成 `.json` 格式的结果文件，其中包含了详细的执行时间统计信息。

**收集其他指标（能耗、CPU、内存）：**

*   **执行时间：** `pyperf.Runner` 会自动为你收集和分析。
*   **能耗 (Energy Usage):**
    *   **Linux:** 可以使用 `perf stat -e power/energy-cores/ ... python your_script.py` (需要硬件支持) 或 `powerstat`。
    *   **Intel CPU:** 可以使用 `Intel Power Gadget` (跨平台桌面应用)。
    *   **估算：** 也可以使用像 `CodeCarbon` 这样的库进行估算，但这通常不如直接硬件测量精确。
    *   **操作方法：** 在启动 `run_benchmarks.py` 的同时，在另一个终端启动能耗监控工具，记录整个脚本运行期间的能耗数据，或者分别运行原始和优化脚本并记录。
*   **CPU 利用率 (CPU Utilisation):**
    *   **Linux/macOS:** `top`, `htop`, `ps aux | grep python`。
    *   **Windows:** 任务管理器。
    *   **操作方法：** 在运行 `run_benchmarks.py` 时，在另一个终端监控Python进程的CPU使用率。
*   **内存使用 (Memory Usage):**
    *   **Python 库：** `memory_profiler` (`pip install memory_profiler`)。它允许你通过装饰器 `@profile` 来精确测量函数的内存使用，或者通过 `mprof run your_script.py` 来分析。
    *   **操作系统工具：** `top`, `htop` (查看RES/RSS列), `ps aux | grep python`。
    *   **操作方法：** 可以通过修改 `float_original.py` 和 `float_optimized_g5.py` 中的 `benchmark` 函数，为其添加 `@profile` 装饰器，然后用 `memory_profiler` 运行。或者，同样在另一个终端用系统工具监控Python进程的内存使用。

### 5. 分析和报告

*   **`pyperf` 结果：** 使用 `pyperf compare_to ref.json new.json` 命令来比较两个 `.json` 结果文件，它会清晰地展示执行时间的百分比变化。
*   **其他指标：** 将你手动收集的能耗、CPU、内存数据整理成表格或图表，直观地比较原始版本和优化版本之间的差异。

通过以上步骤，你就可以针对 `float.py` 这个基准测试，系统地应用你选择的能效指导原则，并定量地评估其效果了。

---

**Motivation:** You have a pre-compiled set of Python energy-efficiency guidelines, categorized into seven families (Code Optimization, Multithreading, Native Code, Function Calls, Object Orientation, Networking, and Other), which are available on GitHub. While there's a belief in their potential, their real-world impact on Python program energy consumption hasn't been thoroughly evaluated. This project aims to fill that gap by measuring these effects.

**Goal:** The primary objective is to compare the energy usage benefits (or drawbacks) that result from applying different families of these guidelines to Python code.

**Experiment Sketch (Steps you need to follow):**

1.  **Select Guidelines:** You must choose at least two distinct families of guidelines from your collection, ensuring you select a minimum of 8 individual guidelines in total.
2.  **Choose Benchmark Code:** You need to select a set of Python code from widely used benchmarks (such as pyperformance, TheAlgorithms, or 30-Days-of-Python). You can either use the entire suite or a representative subset, but it must include at least 10 functions.
3.  **Apply Guidelines:**
    *   Apply the selected energy-efficiency guidelines to the chosen benchmark code.
    *   Crucially, the modified code must retain the exact same functionality as the original code.
    *   You are required to test the modified code, using benchmark test cases if they are available, to ensure functional equivalence.
4.  **Run Experiments:** Execute both the original (unmodified) and the guideline-modified versions of the code.
5.  **Profile Metrics:** During the execution, you will need to profile and measure the following metrics for both versions of the code:
    *   Energy Usage
    *   Execution Time
    *   CPU Usage
    *   Memory Usage