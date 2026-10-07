import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def write_manifest(path, manifest):
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def execute(suite, resume):
    manifest_path = suite / "suite_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["status"] = "running"
    scripts = Path(__file__).resolve().parent
    for model in manifest["models"]:
        output = suite / f"{model}_{manifest['device']}_{manifest['precision']}_b{manifest['batch_size']}"
        previous = [item for item in manifest["outcomes"] if item["model"] == model]
        if previous:
            if not resume:
                raise ValueError(f"Existing outcome requires --resume: {model}")
            print(json.dumps({"retained_previous_outcome": previous[0]}), flush=True)
            continue
        print(json.dumps({"starting_model": model, "output": str(output)}), flush=True)
        if output.exists():
            if not resume:
                raise ValueError(f"Existing run requires --resume: {output}")
            run_manifest = json.loads((output / "run_manifest.json").read_text(encoding="utf-8"))
            if run_manifest["status"] == "running":
                raise RuntimeError(f"Cannot resume an unfinished/running attempt: {output}")
            returncode = 0 if run_manifest["status"] == "complete" else 1
        else:
            command = [sys.executable, "-u", str(scripts / "run_candidate.py"), "--model", model,
                       "--device", manifest["device"], "--precision", manifest["precision"],
                       "--batch-size", str(manifest["batch_size"]), "--output", str(output)]
            returncode = subprocess.run(command, check=False).returncode
        outcome = {"model": model, "output": str(output), "run_exit_code": returncode,
                   "at": datetime.now(timezone.utc).isoformat()}
        if returncode == 0:
            result = subprocess.run([sys.executable, "-u", str(scripts / "verify_candidate.py"), str(output)], check=False)
            outcome.update(status="complete" if result.returncode == 0 else "verification_failed", verification_exit_code=result.returncode)
        else:
            outcome["status"] = "failed"
            failure_path = output / "failure.json"
            if failure_path.exists():
                outcome["failure"] = json.loads(failure_path.read_text(encoding="utf-8"))
        manifest["outcomes"].append(outcome)
        write_manifest(manifest_path, manifest)
        print(json.dumps({"model_outcome": outcome}), flush=True)
    manifest.update(status="complete" if all(item["status"] == "complete" for item in manifest["outcomes"]) else "completed_with_failures",
                    finished_at=datetime.now(timezone.utc).isoformat())
    write_manifest(manifest_path, manifest)
    print(json.dumps({"suite_finished": str(suite), "status": manifest["status"]}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("suite", type=Path)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    execute(args.suite.resolve(), args.resume)
