#!/usr/bin/env python3
"""Example experiment application that uses the WEI client to run a workflow."""

import json
from pathlib import Path

from wei import ExperimentClient


def main() -> None:
    """Runs an example WEI workflow"""
    # This defines the Experiment object that will communicate with the WEI server
    exp = ExperimentClient("localhost", "8000", "Example_Program")

    wf_dir = (Path(__file__).parent.parent / "workflows").resolve()

    wf_run = exp.start_run(
        wf_dir / "open_door.workflow.yaml",
    )
    print(wf_run)

    # This runs the workflow
    wf_run = exp.start_run(
        wf_dir / "pick_tube_rack.workflow.yaml",
    )
    print(wf_run)

    wf_run = exp.start_run(
        wf_dir / "place_tube_rack_with_safe_approach.workflow.yaml",
    )
    print(wf_run)

    wf_run = exp.start_run(
        wf_dir / "close_door.workflow.yaml",
    )
    print(wf_run)


if __name__ == "__main__":
    main()
