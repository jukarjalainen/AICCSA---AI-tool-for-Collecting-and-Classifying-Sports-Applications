import argparse
import os
import re
import sys
import subprocess
from typing import List, Optional


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
APPLE_SCRIPT = os.path.join(THIS_DIR, "enrich_apple_compatibility.py")
ANDROID_SCRIPT = os.path.join(THIS_DIR, "enrich_android_compatibility.py")


def derive_output_paths(input_xlsx: str, apple_out: Optional[str], android_out: Optional[str]):
    base, ext = os.path.splitext(input_xlsx)
    if apple_out is None:
        apple_out = re.sub(r"\.xlsx$", "_compat.xlsx", input_xlsx, flags=re.I)
    if android_out is None:
        android_out = re.sub(r"\.xlsx$", "_android_compat.xlsx", input_xlsx, flags=re.I)
    return apple_out, android_out


def build_apple_args(python: str, input_xlsx: str, sheet: Optional[str], delay: float, blank_nontrue: bool,
                     resume: bool, limit: int, cache_dir: Optional[str], output_xlsx: str) -> List[str]:
    args: List[str] = [python, APPLE_SCRIPT, input_xlsx]
    # Output to specific xlsx
    args += ["--output-xlsx", output_xlsx]
    if sheet:
        args += ["--input-sheet", sheet]
    if blank_nontrue:
        args += ["--blank-nontrue"]
    if resume:
        args += ["--resume"]
    if limit and limit > 0:
        args += ["--limit", str(limit)]
    if delay is not None:
        args += ["--delay", str(delay)]
    if cache_dir:
        args += ["--cache-dir", cache_dir]
    return args


def build_android_args(python: str, input_xlsx: str, sheet: Optional[str], delay: float, blank_nontrue: bool,
                       resume: bool, limit: int, cache_dir: Optional[str], output_xlsx: str, render: bool) -> List[str]:
    args: List[str] = [python, ANDROID_SCRIPT, input_xlsx]
    # Output to specific xlsx
    args += ["--output-xlsx", output_xlsx]
    if sheet:
        args += ["--input-sheet", sheet]
    if blank_nontrue:
        args += ["--blank-nontrue"]
    if resume:
        args += ["--resume"]
    if render:
        args += ["--render"]
    if limit and limit > 0:
        args += ["--limit", str(limit)]
    if delay is not None:
        args += ["--delay", str(delay)]
    if cache_dir:
        args += ["--cache-dir", cache_dir]
    return args


def run_cmd(args: List[str]) -> int:
    print("Running:", " ".join(f'"{a}"' if " " in a else a for a in args))
    proc = subprocess.Popen(args)
    return proc.wait()


def run_parallel(cmd1: List[str], cmd2: List[str]) -> int:
    print("Starting Apple and Android enrichers in parallel...")
    p1 = subprocess.Popen(cmd1)
    p2 = subprocess.Popen(cmd2)
    c1 = p1.wait()
    c2 = p2.wait()
    print(f"Apple exit code: {c1}, Android exit code: {c2}")
    # Return non-zero if either failed
    return 0 if (c1 == 0 and c2 == 0) else 1


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run Apple and Android compatibility enrichers (sequentially by default or in parallel with --parallel).")
    parser.add_argument("input_xlsx", nargs="?", default=os.path.join(os.path.dirname(THIS_DIR), "appsCombinedXLSX.xlsx"), help="Path to the input XLSX (default: ../appsCombinedXLSX.xlsx)")
    parser.add_argument("--sheet", dest="sheet", default=None, help="XLSX sheet name to read (default: first sheet)")
    parser.add_argument("--delay", dest="delay", type=float, default=0.6, help="Delay in seconds between requests (default 0.6)")
    parser.add_argument("--limit", dest="limit", type=int, default=0, help="Process only the first N URLs on each platform (testing)")
    parser.add_argument("--resume", dest="resume", action="store_true", help="Skip rows already fully populated")
    parser.add_argument("--blank-nontrue", dest="blank_nontrue", action="store_true", help="Blank cells that are not True in target columns")
    parser.add_argument("--render", dest="render", action="store_true", help="Enable headless rendering for Android pages")
    parser.add_argument("--apple-cache", dest="apple_cache", default=os.path.join("cache", "apple_pages"), help="Cache dir for Apple pages")
    parser.add_argument("--android-cache", dest="android_cache", default=os.path.join("cache", "google_pages"), help="Cache dir for Google Play pages")
    parser.add_argument("--apple-output", dest="apple_out", default=None, help="Output XLSX path for Apple enrichment (default: <input>_compat.xlsx)")
    parser.add_argument("--android-output", dest="android_out", default=None, help="Output XLSX path for Android enrichment (default: <input>_android_compat.xlsx)")
    parser.add_argument("--parallel", dest="parallel", action="store_true", help="Run Apple and Android enrichers simultaneously")

    args = parser.parse_args(argv)

    # Validate input
    if not os.path.isfile(args.input_xlsx):
        print(f"Input not found: {args.input_xlsx}", file=sys.stderr)
        return 2

    apple_out, android_out = derive_output_paths(args.input_xlsx, args.apple_out, args.android_out)

    py = sys.executable or "python"

    apple_cmd = build_apple_args(py, args.input_xlsx, args.sheet, args.delay, args.blank_nontrue,
                                 args.resume, args.limit, args.apple_cache, apple_out)
    android_cmd = build_android_args(py, args.input_xlsx, args.sheet, args.delay, args.blank_nontrue,
                                     args.resume, args.limit, args.android_cache, android_out, args.render)

    if args.parallel:
        return run_parallel(apple_cmd, android_cmd)
    else:
        print("Running Apple enrichment (sequential mode)...")
        c1 = run_cmd(apple_cmd)
        if c1 != 0:
            return c1
        print("Running Android enrichment (sequential mode)...")
        c2 = run_cmd(android_cmd)
        return c2


if __name__ == "__main__":
    raise SystemExit(main())
