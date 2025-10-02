from EventManager.Models.RunnerEvents import RunnerEvents
from EventManager.EventSubscriptionController import EventSubscriptionController
from ConfigValidator.Config.Models.RunTableModel import RunTableModel
from ConfigValidator.Config.Models.FactorModel import FactorModel
from ConfigValidator.Config.Models.RunnerContext import RunnerContext
from ConfigValidator.Config.Models.OperationType import OperationType
from ProgressManager.Output.OutputProcedure import OutputProcedure as output

from pathlib import Path
from os.path import dirname, realpath
import subprocess
import shlex
import pandas as pd
import numpy as np
import itertools

class RunnerConfig:

    ROOT_DIR = Path(dirname(realpath(__file__)))
    name: str = "pi_orchestrated_runner_1"
    results_output_path: Path = ROOT_DIR / "experiments"
    operation_type: OperationType = OperationType.AUTO
    time_between_runs_in_ms: int = 2000

    # 🔑 Remote test machine
    REMOTE_HOST = "an@10.42.0.1"
    REMOTE_TMP = "/tmp/energibridge.csv"
    REMOTE_ROOT_DIR = "/home/an/Desktop/greenlab/green-lab-project/benchmarks"

    def __init__(self):
        self.benchmark_scripts = {}
        self.profiler = None

        EventSubscriptionController.subscribe_to_multiple_events([
            (RunnerEvents.BEFORE_EXPERIMENT, self.before_experiment),
            (RunnerEvents.BEFORE_RUN, self.before_run),
            (RunnerEvents.START_RUN, self.start_run),
            (RunnerEvents.START_MEASUREMENT, self.start_measurement),
            (RunnerEvents.INTERACT, self.interact),
            (RunnerEvents.STOP_MEASUREMENT, self.stop_measurement),
            (RunnerEvents.STOP_RUN, self.stop_run),
            (RunnerEvents.POPULATE_RUN_DATA, self.populate_run_data),
            (RunnerEvents.AFTER_EXPERIMENT, self.after_experiment),
        ])

        output.console_log("Raspberry Pi orchestrated config loaded")

    def create_run_table_model(self) -> RunTableModel:
        """Discover scripts remotely and build a run table with exclusions for missing combos."""
        allowed_versions = {"baseline", "opt"}.union({f"g{i}" for i in range(1, 10)})
        sizes = ["small", "large"]

        # Run find remotely to discover benchmark scripts
        ssh_cmd = f"ssh {self.REMOTE_HOST} 'find {self.REMOTE_ROOT_DIR} -name \"*.py\"'"
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
        remote_scripts = result.stdout.splitlines()

        found_benchmarks, found_versions = set(), set()

        for script in remote_scripts:
            script_path = Path(script)
            if script_path.name == "__init__.py":
                continue
            parts = script_path.stem.rsplit("_", 1)
            if len(parts) == 2:
                benchmark_name, version_id = parts
                if version_id in allowed_versions:
                    found_benchmarks.add(benchmark_name)
                    found_versions.add(version_id)
                    self.benchmark_scripts[(benchmark_name, version_id)] = script
                    output.console_log(f"  Found valid benchmark: '{benchmark_name}', version: '{version_id}'")

        if not self.benchmark_scripts:
            raise FileNotFoundError("No benchmark scripts found on remote test PC!")

        # Factor models
        benchmark_factor = FactorModel("benchmark", sorted(list(found_benchmarks)))
        version_factor = FactorModel("version", sorted(list(allowed_versions)))
        size_factor = FactorModel("size", sizes)

        # Determine invalid combos
        all_possible = set(itertools.product(found_benchmarks, allowed_versions))
        valid_pairs = set(self.benchmark_scripts.keys())
        invalid_pairs = all_possible - valid_pairs

        exclusion_list = []
        for b_name, v_id in invalid_pairs:
            exclusion_list.append({
                benchmark_factor: [b_name],
                version_factor: [v_id]
            })

        output.console_log(f"Found {len(invalid_pairs)} invalid (benchmark, version) combos to exclude.")

        self.run_table_model = RunTableModel(
            factors=[benchmark_factor, version_factor, size_factor],
            exclude_combinations=exclusion_list,
            data_columns=["exec_time_sec", "cpu_energy_j", "avg_cpu_usage", "avg_used_memory"],
            repetitions=10
        )
        return self.run_table_model

    def before_experiment(self) -> None:
        subprocess.run(f"ssh {self.REMOTE_HOST} 'sync; echo 3 | sudo tee /proc/sys/vm/drop_caches'", shell=True)

    def before_run(self) -> None:
        pass

    def start_run(self, context: RunnerContext) -> None:
        output.console_log(f"Starting run: {context.execute_run}")

    def start_measurement(self, context: RunnerContext) -> None:
        benchmark, version, size = context.execute_run["benchmark"], context.execute_run["version"], context.execute_run["size"]
        script_key = (benchmark, version)
        script_path = self.benchmark_scripts.get(script_key)

        if not script_path:
            output.console_log(f"⚠️ Skipping run: No script found for {script_key}", style="yellow")
            self.profiler = None
            return

        profiler_cmd = (
            f"ssh {self.REMOTE_HOST} "
            f"\"echo '001128' | sudo -S energibridge --interval 5 --output {self.REMOTE_TMP} "
            f"--summary python3 {script_path} --size {size} > /tmp/benchmark_output.log 2>&1\""
        )

        output.console_log(f"Running remotely: {profiler_cmd}")
        self.profiler = subprocess.Popen(profiler_cmd, shell=True)

    def interact(self, context: RunnerContext) -> None:
        if self.profiler:
            self.profiler.wait()
            local_csv = context.run_dir / "energibridge.csv"
            subprocess.run(f"scp {self.REMOTE_HOST}:{self.REMOTE_TMP} {local_csv}", shell=True)
            subprocess.run(f"scp {self.REMOTE_HOST}:/tmp/benchmark_output.log {context.run_dir}/benchmark_output.log", shell=True)

    def stop_measurement(self, context: RunnerContext) -> None:
        if self.profiler and self.profiler.poll() is None:
            self.profiler.terminate()

    def stop_run(self, context: RunnerContext) -> None:
        pass

    def after_experiment(self) -> None:
        pass

    def populate_run_data(self, context: RunnerContext) -> dict:
        file_path = context.run_dir / "energibridge.csv"
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
        avg_cpu_usage = df[[f"CPU_USAGE_{i}" for i in range(12) if f"CPU_USAGE_{i}" in df]].mean(axis=1).mean()
        avg_memory = df["USED_MEMORY"].mean()

        return {
            "exec_time_sec": round(exec_time, 4),
            "cpu_energy_j": round(cpu_energy, 4),
            "avg_cpu_usage": round(avg_cpu_usage, 2),
            "avg_used_memory": round(avg_memory, 2)
        }
