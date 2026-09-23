import os
from datetime import datetime


def start_execution_log(log_file="logs/automation.log"):
    """
    Returns the current size of the log file.
    This position marks where the current execution starts.
    """

    if not os.path.exists(log_file):
        return 0

    return os.path.getsize(log_file)


def create_execution_log(
    start_position,
    log_file="logs/automation.log"
):
    """
    Creates a separate text file containing
    only the logs generated during the current execution.
    """

    os.makedirs("logs/executions", exist_ok=True)

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    execution_file = (
        f"logs/executions/"
        f"execution_{timestamp}.txt"
    )

    try:

        with open(
            log_file,
            "r",
            encoding="utf-8"
        ) as source:

            # Move to the position where this execution started
            source.seek(start_position)

            current_execution_log = source.read()

        with open(
            execution_file,
            "w",
            encoding="utf-8"
        ) as destination:

            destination.write(
                current_execution_log
            )

        print(
            f"Execution log created: "
            f"{execution_file}"
        )

        return execution_file

    except Exception as e:

        print(
            f"Failed to create execution log: {e}"
        )

        return None