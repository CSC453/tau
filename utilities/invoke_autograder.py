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
    args.use_best
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
            # minutes = max(minutes, 0)
            previous_submissions: list[dict[str, Any]] = submission[
                "previous_submissions"
            ]
            if minutes > 0:
                print(f"Minutes late: {minutes}")
            else:
                print(f"Minutes early: {-minutes}")
            previous_score = 0.0
            if len(previous_submissions) > 0:
                most_recent = max(
                    previous_submissions, key=lambda x: x["submission_time"]
                )
                previous_score = float(most_recent["score"])
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
    print(f"Found grader: {found}")
    assert found is not None, f"{graders}"

    use_best: bool = args.use_best or ("use_best" in found and found["use_best"])
    if not use_best:
        previous_score = 0.0

    output: str
    if args.output:
        output = args.output
    else:
        output = "/autograder/results/results.json"
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
            threshold: Optional[float] = (
                found["threshold"] if "threshold" in found else None
            )
            do_gradescope(inputs, output, threshold, minutes, previous_score)
        case _:
            raise NotImplementedError(f"Unknown tester type: {found['tester']}")


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
    parser.add_argument(
        "--use_best", action="store_true", default=False, help="Use best score so far"
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
