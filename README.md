# Empirical assessment of guidelines to write energy-efficient Python code.

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