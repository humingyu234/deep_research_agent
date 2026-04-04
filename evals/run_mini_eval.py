from pathlib import Path

import run_eval as full_eval


ROOT = Path(__file__).resolve().parent


def main() -> None:
    full_eval.TEST_CASES_PATH = ROOT / "mini_eval_cases.json"
    full_eval.EVAL_SUMMARIES_DIR = ROOT / "mini_eval_summaries"
    full_eval.EVAL_RUNS_DIR = ROOT / "mini_eval_runs"
    full_eval.BASELINES_DIR = ROOT / "mini_baselines"
    full_eval.RETAIN_RECENT_EVALS = 5
    full_eval.main()


if __name__ == "__main__":
    main()
