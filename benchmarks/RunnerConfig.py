from EventManager.Models.RunnerEvents import RunnerEvents
from EventManager.EventSubscriptionController import EventSubscriptionController
from ConfigValidator.Config.Models.RunTableModel import RunTableModel
from ConfigValidator.Config.Models.FactorModel import FactorModel
from ConfigValidator.Config.Models.RunnerContext import RunnerContext
from ConfigValidator.Config.Models.OperationType import OperationType
from ProgressManager.Output.OutputProcedure import OutputProcedure as output

from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from os.path import dirname, realpath

import os
import signal
import pandas as pd
import time
import subprocess
import shlex
import numpy as np

class RunnerConfig:

    ROOT_DIR = Path(dirname(realpath(__file__)))

    name: str = "B"
    results_output_path: Path = ROOT_DIR / 'experiments'
    operation_type: OperationType = OperationType.AUTO
    time_between_runs_in_ms: int = 2000

    def __init__(self):
        """Executes immediately after program start, on config load"""

        # This dictionary will map (benchmark, version) tuples to their script Path
        self.benchmark_scripts: Dict[Tuple[str, str], Path] = {}

        EventSubscriptionController.subscribe_to_multiple_events([
            (RunnerEvents.BEFORE_EXPERIMENT, self.before_experiment),
            (RunnerEvents.BEFORE_RUN       , self.before_run       ),
            (RunnerEvents.START_RUN        , self.start_run        ),
            (RunnerEvents.START_MEASUREMENT, self.start_measurement),
            (RunnerEvents.INTERACT         , self.interact         ),
            (RunnerEvents.STOP_MEASUREMENT , self.stop_measurement ),
            (RunnerEvents.STOP_RUN         , self.stop_run         ),
            (RunnerEvents.POPULATE_RUN_DATA, self.populate_run_data),
            (RunnerEvents.AFTER_EXPERIMENT , self.after_experiment )
        ])
        self.run_table_model = None  # Initialized later
        output.console_log("Custom config loaded")

    def create_run_table_model(self) -> RunTableModel:
        """
        Dynamically discovers benchmark scripts and creates a precise run table
        by telling the RunTableModel which combinations to exclude.
        """
        # Import itertools at the top of your RunnerConfig.py file
        import itertools
        
        allowed_versions = {'baseline', 'opt'}.union({f'g{i}' for i in range(1, 10)})
        sizes = ["small", "large"]

        found_benchmarks = set()
        found_versions = set()
        valid_script_filenames = []

        output.console_log("Scanning for benchmark scripts with valid suffixes...")
        for script_path in self.ROOT_DIR.rglob('*.py'):
            if script_path.samefile(__file__) or script_path.name == '__init__.py':
                continue

            parts = script_path.stem.rsplit('_', 1)
            if len(parts) == 2:
                benchmark_name, version_id = parts
                if version_id in allowed_versions:
                    found_benchmarks.add(benchmark_name)
                    found_versions.add(version_id)
                    self.benchmark_scripts[(benchmark_name, version_id)] = script_path
                    valid_script_filenames.append(script_path.name)
        
        # This part for writing to valid.txt remains the same.
        output_file_path = self.ROOT_DIR / 'valid.txt'
        try:
            with open(output_file_path, 'w') as f:
                for filename in sorted(valid_script_filenames):
                    f.write(f"{filename}\n")
            output.console_log(f"Wrote {len(valid_script_filenames)} valid script names to {output_file_path}")
        except IOError as e:
            output.console_log(f"Error writing to {output_file_path}: {e}", style="red")

        if not self.benchmark_scripts:
            raise FileNotFoundError("No benchmark scripts found with valid suffixes!")

        # --- NEW LOGIC START ---

        # Step 1: Define the FactorModels for the complete theoretical grid
        benchmark_factor = FactorModel("benchmark", sorted(list(found_benchmarks)))
        version_factor = FactorModel("version", sorted(list(found_versions)))
        size_factor = FactorModel("size", sizes)
        
        all_factors = [benchmark_factor, version_factor, size_factor]

        # Step 2: Determine which combinations do NOT exist and should be excluded.
        # Get all theoretically possible (benchmark, version) pairs
        all_possible_pairs = set(itertools.product(found_benchmarks, found_versions))
        
        # Get the pairs that actually exist
        valid_pairs = set(self.benchmark_scripts.keys())
        
        # The difference is the set of pairs we need to exclude
        invalid_pairs = all_possible_pairs - valid_pairs
        
        # Step 3: Format the invalid pairs into the structure required by 'exclude_combinations'
        exclusion_list = []
        for b_name, v_id in invalid_pairs:
            rule = {
                benchmark_factor: [b_name],
                version_factor: [v_id]
            }
            exclusion_list.append(rule)
            
        output.console_log(f"Found {len(invalid_pairs)} invalid (benchmark, version) combinations to exclude.")

        # Step 4: Create the RunTableModel using the 'exclude_combinations' parameter
        self.run_table_model = RunTableModel(
            factors=all_factors,
            exclude_combinations=exclusion_list,
            data_columns=["exec_time_sec", "cpu_energy_j", "avg_cpu_usage", "avg_used_memory"],
            repetitions=1
        )
        
        # --- NEW LOGIC END ---
        
        return self.run_table_model

    def before_experiment(self) -> None:
        subprocess.run("sync; echo 3 | sudo tee /proc/sys/vm/drop_caches", shell=True, check=False)

    def before_run(self) -> None:
        """Perform any activity required before starting a run.
        No context is available here as the run is not yet active (BEFORE RUN)"""
        pass

    def start_run(self, context: RunnerContext) -> None:
        print(f"Starting run: {context.execute_run}")

    def start_measurement(self, context: RunnerContext) -> None:
        benchmark = context.execute_run["benchmark"]
        version = context.execute_run["version"]
        size = context.execute_run["size"]

        # Find the script path from the dictionary populated during startup
        script_key = (benchmark, version)
        script_path = self.benchmark_scripts.get(script_key)

        # If no script exists for this factor combination, skip the run
        if not script_path:
            output.console_log(f"Skipping run: No script found for benchmark='{benchmark}', version='{version}'", style="yellow")
            # Start a dummy process that exits immediately to prevent errors later
            self.profiler = subprocess.Popen(["true"])
            return

        profiler_cmd = f'sudo energibridge --interval 100 --output {context.run_dir / "energibridge.csv"} ' \
                       f'--summary python3 {script_path} --size {size}'

        print(f"Running: {profiler_cmd}")
        energibridge_log = open(f"{context.run_dir}/energibridge.log", "w")
        self.profiler = subprocess.Popen(shlex.split(profiler_cmd), stdout=energibridge_log)

    def interact(self, context: RunnerContext) -> None:
        if self.profiler:
            self.profiler.wait()

    def stop_run(self, context: RunnerContext) -> None:
        """Perform any activity here required for stopping the run.
        Activities after stopping the run should also be performed here."""
        pass

    def stop_measurement(self, context: RunnerContext) -> None:
        if self.profiler and self.profiler.poll() is None:
            self.profiler.terminate()

    def after_experiment(self) -> None:
        pass

    def populate_run_data(self, context: RunnerContext) -> dict:
        file_path = context.run_dir / "energibridge.csv"

        # If the output file doesn't exist, the run was likely skipped.
        # Return NaN for all data columns.
        if not file_path.exists():
            output.console_log(f"Warning: No energibridge output at {file_path}. Populating with NaN.", style="yellow")
            return {
                "exec_time_sec": np.nan,
                "cpu_energy_j": np.nan,
                "avg_cpu_usage": np.nan,
                "avg_used_memory": np.nan
            }

        df = pd.read_csv(file_path)
        cpu_energy = df["CPU_ENERGY (J)"].iloc[-1] - df["CPU_ENERGY (J)"].iloc[0]
        exec_time = df["Time"].iloc[-1] - df["Time"].iloc[0]
        avg_cpu_usage = df[[f"CPU_USAGE_{i}" for i in range(12)]].mean(axis=1).mean()
        avg_memory = df["USED_MEMORY"].mean()

        data = {
            "exec_time_sec": round(exec_time, 4),
            "cpu_energy_j": round(cpu_energy, 4),
            "avg_cpu_usage": round(avg_cpu_usage, 2),
            "avg_used_memory": round(avg_memory, 2)
        }

        print(data)
        return data