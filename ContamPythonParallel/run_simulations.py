import os
import sys
import subprocess
import time
import logging
from concurrent.futures import ProcessPoolExecutor

# -----------------------------------------------------------------------------
# Configure global logging: logs will be saved to 'execution.log' and also printed to the console.
log_file = os.path.join(os.getcwd(), 'execution.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# -----------------------------------------------------------------------------
# Update this path to your actual Contam executable.
# For example, if your executable is in the same directory as this script, you might use:
CONTAM_EXE = os.path.join(sys.path[0], 'contamx3.exe')
if not os.path.exists(CONTAM_EXE):
    logging.error(f"Contam executable not found: {CONTAM_EXE}")
    sys.exit(1)

# -----------------------------------------------------------------------------
# List of simulation project files. Ensure these files exist in the 'simulations' folder.
SIMULATION_FILES = [
    os.path.join("simulations", "sim1.prj"),
    os.path.join("simulations", "sim2.prj"),
    os.path.join("simulations", "sim3.prj"),
]

def run_contam(sim_file):
    """
    Runs a single Contam simulation and logs detailed execution information.
    Logs include the command executed, elapsed time, stdout, stderr, and any errors.
    """
    simulation_name = os.path.basename(sim_file)
    logging.info(f"Starting simulation for {simulation_name}")

    # Check if the simulation file exists.
    if not os.path.exists(sim_file):
        error_message = f"Simulation file not found: {sim_file}"
        logging.error(error_message)
        return f"{simulation_name}: File not found"

    # Construct the command to run.
    command = [CONTAM_EXE, sim_file]
    logging.debug(f"Executing command: {' '.join(command)}")

    start_time = time.time()
    try:
        # Run the simulation. Setting cwd=os.getcwd() to ensure the working directory is correct.
        result = subprocess.run(command, capture_output=True, text=True, cwd=os.getcwd())
    except Exception as e:
        logging.exception(f"Exception occurred while running simulation {simulation_name}: {e}")
        return f"{simulation_name}: Exception occurred"

    elapsed_time = time.time() - start_time
    logging.info(f"Finished simulation for {simulation_name} in {elapsed_time:.2f} seconds")

    # Prepare detailed log information.
    log_details = (
        f"Command: {' '.join(command)}\n"
        f"Elapsed Time: {elapsed_time:.2f} seconds\n"
        f"Return Code: {result.returncode}\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}\n"
    )

    # Write detailed log for this simulation to a file in the 'output' folder.
    output_log_file = os.path.join("output", simulation_name.replace(".prj", ".log"))
    try:
        with open(output_log_file, "w", encoding="utf-8") as f:
            f.write(log_details)
        logging.debug(f"Log details for {simulation_name} written to {output_log_file}")
    except Exception as e:
        logging.error(f"Error writing log file for {simulation_name}: {e}")

    return f"{simulation_name}: Completed in {elapsed_time:.2f} seconds, Return Code: {result.returncode}"

def main():
    # Create the output folder if it doesn't exist.
    if not os.path.exists("output"):
        os.makedirs("output")
        logging.debug("Created 'output' directory.")

    logging.info("Starting all simulations in parallel.")
    with ProcessPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(run_contam, SIMULATION_FILES))

    logging.info("All simulations completed. Summary:")
    for res in results:
        logging.info(res)

if __name__ == '__main__':
    main()
