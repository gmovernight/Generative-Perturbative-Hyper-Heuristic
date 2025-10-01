#!/usr/bin/env python3
"""
demo_gphh.py — quick usage demo for Generation Perturbative Hyper-Heuristic (disposable only)

Examples:
  python demo_gphh.py --obj f13_D10 --seed 7 --pop 60 --gens 20 --per-prog 3000 --evals 200000 --verbose
  python demo_gphh.py --obj f1 --seed 1 --pop 30 --gens 10 --per-prog 1000 --evals 50000
"""
import argparse
import os, sys, time

try:
    from benchmark_functions import OBJECTIVES
    from gphh import GPHH
except Exception:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from benchmark_functions import OBJECTIVES
    from gphh import GPHH

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--obj", type=str, default="f13_D10", help="Objective key from benchmark_functions.OBJECTIVES")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--pop", type=int, default=60, help="GP population size")
    ap.add_argument("--gens", type=int, default=20, help="GP generations")
    ap.add_argument("--per-prog", type=int, default=3000, help="Budget per program during evolution")
    ap.add_argument("--evals", type=int, default=200000, help="Final max evaluations to apply best program")
    ap.add_argument("--print-every", type=int, default=1, help="Progress print frequency (generations)")
    ap.add_argument("--verbose", action="store_true", help="Verbose evolution logs")
    args = ap.parse_args()

    if args.obj not in OBJECTIVES:
        print(f"[error] Unknown objective key: {args.obj}")
        print("Available keys (first 20):", ", ".join(list(OBJECTIVES.keys())[:20]), "...")
        sys.exit(1)

    f, lo, hi, D = OBJECTIVES[args.obj]
    print(f"[demo] Objective={args.obj}  D={D}  bounds=[{lo.min():.3g},{hi.max():.3g}]  seed={args.seed}")

    solver = GPHH(
        f, (lo, hi), D,
        seed=args.seed,
        gp_pop=args.pop,
        gp_gens=args.gens,
        eval_budget_per_prog=args.per_prog,
        max_evals=args.evals,
        verbose=args.verbose,
        print_every=args.print_every
    )
    t0 = time.time()
    res = solver.run()
    elapsed = time.time() - t0

    print("\n[demo] Finished.")
    print(f"  best f:     {res.f_best:.6g}")
    print(f"  evals used: {res.evaluations}")
    print(f"  runtime:    {elapsed:.2f} s (incl. evolution)")
    print(f"  program:    {getattr(solver, '_best_prog_desc', '(unavailable)')}")

if __name__ == "__main__":
    main()