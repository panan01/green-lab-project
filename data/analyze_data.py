import pandas as pd

def analyze_experiment_data(file_path):
    try:
        print("--- Loading and Inspecting Data ---")
        df = pd.read_csv(file_path)
        print(f"Successfully loaded {file_path}")
        print(f"Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns")
        print("\nColumn names and data types:")
        print(df.info())

        print("\nChecking for missing values in each column:")
        print(df.isnull().sum())
        print("-" * 50)

        print("\n--- Summarizing Experimental Design ---")
        unique_benchmarks = df['benchmark'].nunique()
        unique_versions = df['version'].unique()
        unique_sizes = df['size'].unique()
        
        print(f"Number of unique benchmarks: {unique_benchmarks}")
        print(f"Versions tested: {unique_versions}")
        print(f"Workload sizes tested: {unique_sizes}")

        repetition_counts = df.groupby(['benchmark', 'version', 'size']).size()
        print(f"\nNumber of repetitions for each experiment (should be consistent):")
        print(f"  - Minimum repetitions for any test: {repetition_counts.min()}")
        print(f"  - Maximum repetitions for any test: {repetition_counts.max()}")
        if repetition_counts.min() != repetition_counts.max():
            print("  - WARNING: Inconsistent number of repetitions found!")
        else:
            print(f"  - All experiments have exactly {repetition_counts.min()} repetitions. This is good!")
        print("-" * 50)

        print("\n--- Descriptive Statistics for Numerical Metrics ---")
        metrics_to_describe = ['cpu_energy_j', 'exec_time_sec', 'avg_cpu_usage', 'avg_used_memory']
        print(df[metrics_to_describe].describe())
        print("-" * 50)

        print("\n--- Outlier Detection for CPU Energy (cpu_energy_j) ---")
        Q1 = df.groupby(['benchmark', 'version', 'size'])['cpu_energy_j'].transform('quantile', 0.25)
        Q3 = df.groupby(['benchmark', 'version', 'size'])['cpu_energy_j'].transform('quantile', 0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = df[(df['cpu_energy_j'] < lower_bound) | (df['cpu_energy_j'] > upper_bound)]
        outlier_count = len(outliers)

        if outlier_count > 0:
            print(f"Found {outlier_count} potential outliers based on the IQR method.")
            print("This suggests that non-parametric tests (like the Wilcoxon test) are a good choice for hypothesis testing.")
        else:
            print("No significant outliers were detected.")
        print("-" * 50)
        
        print("\n--- Preliminary Comparison: Average Energy Usage (Baseline vs. Opt) ---")
        
        baseline_df = df[df['version'] == 'baseline'].groupby(['benchmark', 'size'])['cpu_energy_j'].mean().reset_index()
        baseline_df.rename(columns={'cpu_energy_j': 'baseline_energy'}, inplace=True)
        
        opt_df = df[df['version'] == 'opt'].groupby(['benchmark', 'size'])['cpu_energy_j'].mean().reset_index()
        opt_df.rename(columns={'cpu_energy_j': 'opt_energy'}, inplace=True)
        
        comparison_df = pd.merge(baseline_df, opt_df, on=['benchmark', 'size'])
        comparison_df['reduction_%'] = ((comparison_df['baseline_energy'] - comparison_df['opt_energy']) / comparison_df['baseline_energy']) * 100
        
        print("Comparison of average energy usage and percentage reduction:")
        pd.set_option('display.max_rows', None)
        print(comparison_df.to_string(index=False))
        pd.reset_option('display.max_rows')
        print("-" * 50)

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        print("Please make sure the script is in the same directory as the CSV file.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    csv_file = 'data/run_table.csv'
    analyze_experiment_data(csv_file)