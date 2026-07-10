import os
import datetime
import json
import argparse
from chatbots import chat_model_triage_manager
from evals import eval_triage_manager

# GLOBAL VARS
DEFAULT_RUNS_PER_TEST = int(os.environ.get("DEFAULT_RUNS_PER_TEST", 1))


# Fetches JSON data for test cases
def test_case_setup(json_file_name: str, targets: list[dict]) -> list[dict]:
    with open(json_file_name, "r") as file:
        cases = json.load(file)

    expanded = []
    for target in targets:
        for case in cases:
            expanded.append({
                **case,
                "id": f"{target['bot']}_{target['model']}_{case['id']}",
                "bot": target["bot"],
                "model": target["model"],
            })
    return expanded


def filter_by_bot(test_cases: list[dict], bot: str | None) -> list[dict]:
    if bot is None:
        return test_cases
    return [t for t in test_cases if t["bot"] == bot]


def filter_by_model(test_cases: list[dict], model: str | None) -> list[dict]:
    if model is None:
        return test_cases
    return [t for t in test_cases if t["model"] == model]


def load_targets(targets_filename: str = "targets.json") -> list[dict]:
    with open(targets_filename, "r") as file:
        return json.load(file)


def load_suite(suite_name: str, suites_filename: str = "suites.json") -> list[str]:
    with open(suites_filename, "r") as file:
        suites = json.load(file)
    if suite_name not in suites:
        raise ValueError(f"Unknown suite '{suite_name}'. Available: {list(suites.keys())}")
    return suites[suite_name]


# Determines the test cases to run and creates a result dict.
# Format: {Test Case ID : pass rate}
def run_test_cases(test_case_dict: dict) -> dict:
    results_dict = {}
    for t in test_case_dict:
        result = process_one_test_case(t)
        results_dict[t["id"]] = result
    return results_dict


def process_one_test_case(test_case: dict) -> dict:
    passed_runs = 0
    failed_runs = 0
    num_runs = test_case.get("num_of_runs_override", DEFAULT_RUNS_PER_TEST)
    if num_runs <= 0:
        raise ValueError(f"Test case '{test_case.get('id')}' has invalid num_runs: {num_runs}")

    for _ in range(num_runs):
        resp = response_from_chatbot(test_case["bot"], test_case["model"], test_case["prompt"])
        resp_eval = evaluate_response_from_chatbot(resp, test_case["invariant_type"],
                                                   test_case[test_case["invariant_type"]])
        if resp_eval:
            passed_runs += 1
        else:
            failed_runs += 1

    pass_rate = round(((passed_runs / num_runs) * 100), 1)
    results = {"bot": test_case["bot"],
               "model": test_case["model"],
               "passes": passed_runs,
               "fails": failed_runs,
               "pass_rate": pass_rate}
    return results


# Receives output from specified bot
def response_from_chatbot(bot: str, model: str, prompt: str) -> str:
    model_response = chat_model_triage_manager.triage_response_from_bot(bot, model, prompt)
    return model_response


# Receives bot response and determines whether it is "correct" by specified invariance
def evaluate_response_from_chatbot(response: str, invariant_type: str, invariant_var) -> bool:
    resp_eval = eval_triage_manager.evaluate_response(response, invariant_type, invariant_var)
    return resp_eval


def create_results_file(results_dict: dict, test_filename: str) -> None:
    os.makedirs("results", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M")
    filename = f"results/{test_filename}_{timestamp}.json"
    output = {
        "run_timestamp": timestamp,
        "results": results_dict
    }

    with open(filename, "w") as file:
        json.dump(output, file, indent=2)
    return


def main(test_case_filenames: list[str], bot: str | None = None, model: str | None = None) -> None:
    targets = load_targets()

    all_results = {}
    for filename in test_case_filenames:
        fetched_tests = test_case_setup(f"test_cases/{filename}.json", targets)
        fetched_tests = filter_by_bot(fetched_tests, bot)
        fetched_tests = filter_by_model(fetched_tests, model)
        all_results[filename] = run_test_cases(fetched_tests)

    label = "_".join(test_case_filenames) if len(test_case_filenames) <= 3 else "multi_suite"
    create_results_file(all_results, label)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run chatbot eval test cases.")
    parser.add_argument("test_case_filenames", nargs="*", default=[],
                        help="Specific test case JSON files to run (without .json)")
    parser.add_argument("--suite", help="Named suite to run, from suites.json")
    parser.add_argument("--bot", help="Only run test cases targeting this bot (e.g. openai, claude)")
    parser.add_argument("--model", help="Only run test cases targeting this model (e.g. gpt-5-nano)")
    args = parser.parse_args()

    if args.suite:
        filenames = load_suite(args.suite)
    elif args.test_case_filenames:
        filenames = args.test_case_filenames
    else:
        parser.error("Provide either test_case_filenames or --suite")

    main(filenames, bot=args.bot, model=args.model)
