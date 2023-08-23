import json
import argparse
import datetime
from typing import Optional, Any

from testerator.gradescope import do_gradescope


def main() -> None:
    args = get_args()
    title: str = ""
    minutes: float = 0.0
    previous_score: float = 0.0
    if args.title:
        title = args.title
    else:
        with open("/autograder/submission_metadata.json", "r") as f:
            submission = json.load(f)
            title = submission["assignment"]["title"]
            due_date: str = submission["assignment"]["due_date"]
            created_at: str = submission["created_at"]
            due_date_time = datetime.datetime.strptime(
                due_date, "%Y-%m-%dT%H:%M:%S.%f%z"
            )
            created_date_time = datetime.datetime.strptime(
                created_at, "%Y-%m-%dT%H:%M:%S.%f%z"
            )
            late: datetime.timedelta = created_date_time - due_date_time
            minutes = late.total_seconds() / 60
            minutes = max(minutes, 0)
            previous_submissions: list[dict[str, Any]] = submission[
                "previous_submissions"
            ]
            print(f"Minutes late: {minutes}")
            previous_score: float = 0.0
            if len(previous_submissions) > 0:
                most_recent = max(
                    previous_submissions, key=lambda x: x["submission_time"]
                )
                previous_score: float = most_recent["score"]
                print(f"Previous score: {previous_score}")

    print(f"Assignment/Milestone title: {title}")
    found: Optional[dict[str, Any]] = None
    with open("./tau/milestones/graders.json", "r") as f:
        graders = json.load(f)
        grader: dict[str, Any]
        for grader in graders["graders"]:
            grader_title: str = grader["name"]
            if title.startswith(grader_title):
                found = grader
                break

    assert found is not None

    if args.output:
        output: str = args.output
    else:
        output: str = "/autograder/results/results.json"
    match found["tester"]:
        case "pass":
            results = {
                "score": 100.0,
                "output": "Test passed",
                "output_format": "simple_format",
                "stdout_visibility": "visible",
            }
            # write results to /autograder/results/results.json
            with open(output, "w") as f:
                json.dump(results, f)
        case "testerator":
            fname = "./tau/milestones/" + found["pickle"]
            inputs: list[str] = [fname]
            threshold: float = found["threshold"]
            do_gradescope(inputs, output, threshold, minutes, previous_score)
        case _:
            raise NotImplementedError(
                f"Unknown tester type: {found['tester']}"
            )


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--title",
        type=str,
        help="Assignment/Milestone name",
        default="",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="JSON output file",
        default="",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
