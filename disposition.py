#!/usr/bin/env python3
"""Run the whole benchmark: every scenario and control, for one or more models.

  ./disposition.py run --url $URL --models qwen3.8-flash,glm-5.2
  ./disposition.py run --url $URL --models glm-5.2 -n 3 --jobs 6
  ./disposition.py run --resume results/2026-09-25_1430     # finish an interrupted batch
  ./disposition.py run --url $URL --models glm-5.2 --only curiosity_,hubris_records
  ./disposition.py grade results/2026-09-25_1430 --judge-model glm-5.2

The API key is read from an environment variable (MODEL_API_KEY by default,
see --key-env) and handed to each episode through the environment, never on a
command line.

Each model is preflighted first; a model that fails preflight is skipped, since
none of its results could be interpreted. Episodes run through Enclosure's
run.py, several at once, slowest scenarios first. Progress is written to
results/<stamp>/run.json after every episode, so an interrupted batch can be
resumed and finished episodes are not paid for twice.
"""
import argparse
import json
import os
import platform
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCENARIOS = HERE / "scenarios"

# Slowest first, so the long ones are not left running alone at the end.
# Reply delays make accommodation and patience take tens of minutes.
SLOW_FIRST = ["accommodation", "patience", "hubris", "sycophancy", "curiosity", "instruction", "creativity"]


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def find_enclosure(arg):
    for c in [arg, os.getenv("ENCLOSURE"), HERE.parent / "enclosure", HERE.parent / "Enclosure"]:
        if c and (Path(c) / "run.py").is_file():
            return Path(c).resolve()
    raise SystemExit("can't find Enclosure; pass --enclosure PATH or set ENCLOSURE")


def git_commit(path):
    try:
        out = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True)
        dirty = subprocess.run(["git", "-C", str(path), "status", "--porcelain"], capture_output=True, text=True)
        return out.stdout.strip() + ("-dirty" if dirty.stdout.strip() else "") if out.returncode == 0 else None
    except FileNotFoundError:
        return None


def scenario_names(only):
    names = sorted(p.name for p in SCENARIOS.iterdir() if (p / "scenario.yaml").is_file())
    if only:
        pats = [o.strip() for o in only.split(",") if o.strip()]
        names = [n for n in names if any(n.startswith(p) for p in pats)]
    rank = {t: i for i, t in enumerate(SLOW_FIRST)}
    return sorted(names, key=lambda n: (rank.get(n.split("_")[0], len(rank)), n))


def read_log(path):
    evs = [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
    start = next((e for e in evs if e["ev"] == "START"), {})
    end = next((e for e in evs if e["ev"] == "END"), None)
    return start, end


class Batch:
    def __init__(self, root, meta):
        self.root = root
        self.path = root / "run.json"
        self.lock = threading.Lock()
        self.data = meta

    def save(self):
        with self.lock:
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.data, indent=2))
            tmp.replace(self.path)

    def done(self, model, scenario, rep):
        return any(
            e["model"] == model and e["scenario"] == scenario and e["rep"] == rep and e["end"] in ("script_complete", "tool_cap")
            for e in self.data["episodes"]
        )

    def add(self, rec):
        with self.lock:
            self.data["episodes"] = [
                e for e in self.data["episodes"]
                if not (e["model"] == rec["model"] and e["scenario"] == rec["scenario"] and e["rep"] == rec["rep"])
            ] + [rec]
        self.save()


def preflight(enc, args, model, env):
    cmd = [sys.executable, str(enc / "preflight.py"), "--model", model, "--json"]
    if args.url:
        cmd += ["--url", args.url]
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=enc)
    try:
        res = json.loads(r.stdout)
    except ValueError:
        res = {"pass": False, "error": (r.stderr or r.stdout)[-500:]}
    return res


def run_one(enc, args, batch, model, scenario, rep, env):
    logs = batch.root / "logs"
    cmd = [sys.executable, str(enc / "run.py"), str(SCENARIOS / scenario), "--model", model, "--out", str(logs)]
    if args.url:
        cmd += ["--url", args.url]
    for flag, val in [("--temperature", args.temperature), ("--seed", args.seed), ("--timeout", args.timeout)]:
        if val is not None:
            cmd += [flag, str(val)]
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=enc)
    rec = {"model": model, "scenario": scenario, "rep": rep, "seconds": round(time.time() - t0),
           "log": None, "end": "runner_error", "scenario_hash": None}
    # run.py prints "[1/1] <path to log>" on success
    for line in r.stderr.splitlines():
        if line.startswith("[") and line.rstrip().endswith(".jsonl"):
            p = Path(line.split("] ", 1)[1].strip())
            start, end = read_log(p)
            rec.update(log=str(p.relative_to(batch.root)), end=(end or {}).get("reason", "no_end"),
                       scenario_hash=start.get("scenario_hash"))
    if rec["end"] == "runner_error":
        rec["error"] = r.stderr[-800:]
    batch.add(rec)
    return rec


def cmd_run(args):
    enc = find_enclosure(args.enclosure)
    key = os.getenv(args.key_env)
    env = dict(os.environ)
    if key:
        env["OPENAI_API_KEY"] = key  # Enclosure's Provider reads this; keeps the key off argv

    if args.resume:
        root = Path(args.resume).resolve()
        data = json.loads((root / "run.json").read_text())
        st = data["settings"]
        args.url, args.n, args.only = st["url"], st["episodes_per_scenario"], st["only"]
        args.temperature, args.seed = st["temperature"], st["seed"]
        args.models = ",".join(st["models"])
        data.setdefault("resumed", []).append(now())
    else:
        if not args.models:
            raise SystemExit("--models is required")
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")
        root = HERE / "results" / stamp
        root.mkdir(parents=True, exist_ok=False)
        data = {
            "started": now(),
            "finished": None,
            "settings": {
                "url": args.url,
                "models": [m.strip() for m in args.models.split(",") if m.strip()],
                "episodes_per_scenario": args.n,
                "only": args.only,
                "temperature": args.temperature,
                "seed": args.seed,
            },
            "machine": {
                "os": platform.platform(),
                "python": platform.python_version(),
            },
            "code": {"enclosure": git_commit(enc), "disposition": git_commit(HERE)},
            "preflight": {},
            "episodes": [],
        }
    batch = Batch(root, data)
    batch.save()
    print(f"batch: {root}", file=sys.stderr)

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    ok_models = []
    for m in models:
        if data["preflight"].get(m, {}).get("pass"):
            ok_models.append(m)
            continue
        res = preflight(enc, args, m, env)
        data["preflight"][m] = {**res, "at": now()}
        batch.save()
        print(f"preflight {m}: {'PASS' if res.get('pass') else 'FAIL -- skipped'}", file=sys.stderr)
        if res.get("pass"):
            ok_models.append(m)

    names = scenario_names(args.only)
    queue = [(m, s, r) for s in names for m in ok_models for r in range(args.n) if not batch.done(m, s, r)]
    total = len(queue)
    print(f"{total} episodes queued ({len(names)} scenarios x {len(ok_models)} models x {args.n})", file=sys.stderr)

    n = 0
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futs = [pool.submit(run_one, enc, args, batch, m, s, r, env) for m, s, r in queue]
        for f in as_completed(futs):
            rec = f.result()
            n += 1
            print(f"[{n}/{total}] {rec['model']:<24} {rec['scenario']:<36} {rec['end']:<16} {rec['seconds']}s",
                  file=sys.stderr)

    data["finished"] = now()
    batch.save()
    bad = [e for e in data["episodes"] if e["end"] not in ("script_complete", "tool_cap")]
    print(f"done: {len(data['episodes']) - len(bad)} ok, {len(bad)} not ok -> {root / 'run.json'}", file=sys.stderr)
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="run every scenario for one or more models")
    r.add_argument("--models", help="comma-separated model names")
    r.add_argument("--url", help="OpenAI-compatible base URL")
    r.add_argument("--key-env", default="MODEL_API_KEY", help="env var holding the API key")
    r.add_argument("-n", type=int, default=1, help="episodes per scenario per model")
    r.add_argument("--jobs", type=int, default=4, help="episodes at once")
    r.add_argument("--only", help="comma-separated scenario name prefixes")
    r.add_argument("--temperature", type=float)
    r.add_argument("--seed", type=int)
    r.add_argument("--timeout", type=float, help="seconds per model request")
    r.add_argument("--enclosure", help="path to the Enclosure checkout")
    r.add_argument("--resume", help="results/<stamp> directory of a batch to finish")
    g = sub.add_parser("grade", help="judge a finished batch and roll up per trait")
    g.add_argument("batch", help="results/<stamp> directory")
    g.add_argument("--judge-model", required=True, help="model that grades, on the batch's URL")
    g.add_argument("--url", help="override the batch's URL")
    g.add_argument("--key-env", default="MODEL_API_KEY", help="env var holding the API key")
    g.add_argument("--jobs", type=int, default=4, help="episodes judged at once")
    g.add_argument("--timeout", type=float, default=600, help="seconds per judge request")
    g.add_argument("--regrade", action="store_true", help="ignore cached grades")
    args = ap.parse_args()
    if args.cmd == "run":
        sys.exit(cmd_run(args))
    if args.cmd == "grade":
        sys.exit(cmd_grade(args))


def cmd_grade(args):
    from harness import Provider

    import grade

    run = json.loads((Path(args.batch) / "run.json").read_text())
    provider = Provider(url=args.url or run["settings"]["url"], model=args.judge_model,
                        api_key=os.getenv(args.key_env), temperature=0, timeout=args.timeout)
    scores = grade.grade_batch(args.batch, provider, jobs=args.jobs, regrade=args.regrade)
    grade.print_table(scores)
    print(f"-> {Path(args.batch) / 'scores.json'}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    main()
