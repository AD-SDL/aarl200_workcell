#!/usr/bin/env python3
"""Example experiment application that uses the WEI client to run a workflow."""

from pathlib import Path

from wei import ExperimentClient


def main() -> None:
    """Runs an example WEI workflow"""
    # This defines the Experiment object that will communicate with the WEI server
    exp = ExperimentClient("localhost", "8000", "ARL200_Demo")

    wf_dir = (Path(__file__).parent.parent / "workflows").resolve()

    while True:
        # wf_run = exp.start_run(
        #     wf_dir / "open_door.workflow.yaml",
        # )

        wf_run = exp.start_run(
            wf_dir / "pick_tube_rack.workflow.yaml",
        )
        break

        # wf_run = exp.start_run(
        #     wf_dir / "place_tube_rack_with_safe_approach.workflow.yaml",
        # )

        # wf_run = exp.start_run(
        #     wf_dir / "close_door.workflow.yaml",
        # )

        # wf_run = exp.start_run(
        #     wf_dir / "move_to_middle.yaml",
        # )

        # wf_run = exp.start_run(
        #     wf_dir / "open_door.workflow.yaml",
        # )

        # wf_run = exp.start_run(
        #     wf_dir / "pick_tube_rack_with_safe_approach.workflow.yaml",
        # )

        # wf_run = exp.start_run(
        #     wf_dir / "place_tube_rack.workflow.yaml",
        # )

        # wf_run = exp.start_run(
        #     wf_dir / "close_door.workflow.yaml",
        # )


if __name__ == "__main__":
    main()
