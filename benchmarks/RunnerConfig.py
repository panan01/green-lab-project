from EventManager.Models.RunnerEvents import RunnerEvents
from EventManager.EventSubscriptionController import EventSubscriptionController
from ConfigValidator.Config.Models.RunTableModel import RunTableModel
from ConfigValidator.Config.Models.FactorModel import FactorModel
from ConfigValidator.Config.Models.RunnerContext import RunnerContext
from ConfigValidator.Config.Models.OperationType import OperationType
from ProgressManager.Output.OutputProcedure import OutputProcedure as output

from typing import Dict, List, Any, Optional
from pathlib import Path
from os.path import dirname, realpath

import os
import signal
import pandas as pd
import time
import subprocess
import shlex

class RunnerConfig:

    ROOT_DIR = Path(dirname(realpath(__file__)))

    name: str = "new_runner_experiment"
    results_output_path: Path = ROOT_DIR / 'experiments'
    operation_type: OperationType = OperationType.AUTO
    time_between_runs_in_ms: int = 2000

    def __init__(self):
        """Executes immediately after program start, on config load"""

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
        benchmark = FactorModel("benchmark", [
            "sum_squares", "string_concat", "sort", "logic", "approx", "temp_storage", "fib", "inline"
        ])
        version = FactorModel("version", ["baseline", "opt"])
        size = FactorModel("size", ["small", "large"])

        self.run_table_model = RunTableModel(
            factors=[benchmark, version, size],
            data_columns=["exec_time_sec", "cpu_energy_j", "avg_cpu_usage", "avg_used_memory"],
            repetitions=10
        )
        return self.run_table_model

    def before_experiment(self) -> None:
        subprocess.run("sync; echo 3 | sudo tee /proc/sys/vm/drop_caches", shell=True)

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
        folder = "baseline" if version == "baseline" else "optimised"
        script_path = self.ROOT_DIR / "benchmarks" / f"{benchmark}_{version}.py"

        profiler_cmd = f'sudo energibridge --interval 100 --output {context.run_dir / "energibridge.csv"} '                        f'--summary python3 {script_path} --size {size}'

        print(f"Running: {profiler_cmd}")
        energibridge_log = open(f"{context.run_dir}/energibridge.log", "w")
        self.profiler = subprocess.Popen(shlex.split(profiler_cmd), stdout=energibridge_log)

    def interact(self, context: RunnerContext) -> None:
        self.profiler.wait()

    def stop_run(self, context: RunnerContext) -> None:
        """Perform any activity here required for stopping the run.
        Activities after stopping the run should also be performed here."""
        pass

    def stop_measurement(self, context: RunnerContext) -> None:
        if self.profiler and self.profiler.poll() is None:
            self.profiler.terminate()

    def after_experiment(self, context: RunnerContext) -> None:
        pass

    def populate_run_data(self, context: RunnerContext) -> dict:
        file_path = context.run_dir / "energibridge.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"No output from EnergyBridge at: {file_path}")

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