# GPHH — Generation Perturbative Hyper‑Heuristic

GP‑evolved perturbation programs for black‑box **minimization** on classic benchmark functions (Wang & Song f1–f24). This repo contains a compact, “disposable‑only” GPHH: it **evolves** small programs built from search primitives, **selects** the best program under a per‑program budget, and then **applies** that program with a larger evaluation budget to solve the target function.

> **Why “perturbative”?** Each program composes simple operators (Gaussian/Cauchy steps, coordinate resets, opposition moves, etc.) with control flow (`SEQ`, `REPEAT`, `IF`) to generate proposals; acceptance uses an SA‑style schedule.

---

## What’s inside

```
gphh.py                   # Core algorithm: GP + interpreter + SA acceptance
benchmark_functions.py    # f1–f24 registry (plus D=10/30/50 variants)
demo_gphh.py              # Minimal end‑to‑end demo for a single objective
run_gphh_suite.py         # Batch runner over many objectives & seeds → CSV
aggregate_gphh_results.py # Aggregate per‑objective stats from the CSV
replay_gphh.py            # Re‑apply learned programs & plot convergence
replay_gphh_by_function.py# Replay/plots grouped by base function across D
```

---

## Quick start

### 1) Environment
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install numpy pandas matplotlib
```

### 2) One‑shot demo
```bash
python demo_gphh.py --obj f13_D10 --seed 7 --pop 60 --gens 20 --per-prog 3000 --evals 200000
```
You’ll see the best value, total evals used, runtime, and a printable program description.

### 3) Batch runs → CSV
```bash
# run all f1..f24 (and any D=10/30/50 variants present) across seeds 1..10
python run_gphh_suite.py --auto --seeds 1..10 --out results/gphh_results.csv   --pop 60 --gens 20 --per-prog 3000 --evals 200000
```
The CSV includes columns such as `obj_key, dim, seed, gp_pop, gp_gens, per_prog, evals, best_f, evals_used, runtime_sec, program_str, status, error`.

### 4) Aggregate summary
```bash
python aggregate_gphh_results.py --input results/gphh_results.csv --output results/gphh_summary.csv
```

### 5) Re‑play learned programs (plots + CSV traces)
```bash
# per objective (best seed per objective by default)
python replay_gphh.py --input results/gphh_results.csv --objs ALL --pick best   --evals 100000 --trace-every 500 --outdir traces

# grouped by base function across dimensions
python replay_gphh_by_function.py --input results/gphh_results.csv --pick best   --evals 100000 --trace-every 500 --outdir traces_by_function
```
Outputs per‑trace CSVs, PNGs, and a combined PDF with one page per objective / function group.

---

## Core idea (in 20 seconds)

```
Initialize GP population of random programs
└─ Each program = composition of primitives with control flow
   (APPLY(op), SEQ(...), REPEAT(k, ...), IF(cond) THEN ... ELSE ...)

For each generation:
  • Evaluate programs under a small budget (SA‑style acceptance)
  • Tournament select → subtree crossover → point/subtree mutation
  • Keep the best program (elitism)

After evolution:
  • Apply the best program with a larger eval budget to solve the objective
```

### Primitive operators (examples)
- `GAUSS_FULL(sigma_rel)` — Gaussian step in all dims  
- `GAUSS_KDIMS(k, sigma_rel)` — Gaussian step in a random subset of dims  
- `CAUCHY_FULL(scale_rel)` — Cauchy step for occasional long jumps  
- `RESET_COORD(p)` — Randomly reset coordinates with prob. *p*  
- `OPP_BLEND(beta)` — Opposition‑based blend with the box‑opposite point  
- `PULL_TO_BEST(rate, jitter_rel)` — Pull toward current best + small jitter

Programs print in a compact textual form, e.g.:
```
SEQ(APPLY(GAUSS_FULL(sigma_rel=0.12)), REPEAT(3, APPLY(RESET_COORD(p=0.2))))
```

---

## Benchmarks

- `benchmark_functions.py` registers Wang & Song (2019) f1–f24 and scalable variants (`_D10`, `_D30`, `_D50`). Each entry maps to `(func, lower_bounds, upper_bounds, dim)`.
- All objectives are **minimization** and respect box constraints.

---

## Results & files

- **Raw runs** → `results/gphh_results.csv` (appended). Each row = one (objective, seed).  
- **Aggregates** → `results/gphh_summary.csv` with per‑objective stats: `runs, best, median, mean, std, mean_runtime_s, median_runtime_s, error_runs`.
- **Replays/plots** → `traces/` and `traces_by_function/` (CSVs, PNGs, PDFs).

Suggested directory layout:
```
.
├── results/
│   ├── gphh_results.csv
│   └── gphh_summary.csv
├── traces/
│   ├── csv/
│   ├── plots/
│   └── replay_convergence.pdf
└── traces_by_function/
    ├── csv/
    ├── plots/
    └── replay_by_function.pdf
```

---

## Command‑line reference (high‑level)

### `demo_gphh.py`
- `--obj` objective key (see `benchmark_functions.py`), e.g. `f13_D10`
- `--pop, --gens` GP population & generations
- `--per-prog` evaluation budget per candidate program during evolution
- `--evals` final (larger) budget to **apply** the best program

### `run_gphh_suite.py`
- `--auto` or `--objs` (`AUTO`, `ALL`, `ALL_D10/30/50`, `fK`, `fK_D*`, `f3_D10,f7_D30`, …)
- `--seeds` (`1..10`, `1,3,7`, …)
- Core hyper‑params: `--pop, --gens, --per-prog, --evals, --depth, --tk, --pcx, --pmut`
- Appends rows to `--out` CSV and prints a compact per‑function plan + ETA

### `aggregate_gphh_results.py`
- `--input` path to the results CSV; `--output` path for the summary CSV

### `replay_gphh.py` / `replay_gphh_by_function.py`
- Require `gphh.apply_program_from_string` to be available. If not, see the header of the replay scripts for the helper signature and add it to `gphh.py` (the parser is included near the end of `gphh.py`).

---

## Reproducibility

- Every run accepts a `--seed`. Internally numpy’s `default_rng(seed)` is used consistently for program generation, operator randomness, and acceptance decisions.
- Objectives are bounded (“box constraints”); all operators clamp to bounds.

---

## Notes & tips

- The disposable design keeps the core compact. If you need a reusable mode (persist & reuse evolved programs across problems), extract the GP/interpreter pieces from `gphh.py` into a library module and add serialization.
- Budgets matter: a larger `--per-prog` encourages deeper programs to shine; a larger `--evals` improves final refinement during application.
- For noisy functions, consider multiple independent seeds and aggregate with the provided scripts.

---

## Acknowledgements

- Benchmark definitions are adapted from classic f1–f24 test functions with a convenient registry and bounds for D = 10/30/50.
- Implementation style: GP with subtree crossover, point/subtree mutation, tournament selection, elitism; acceptance via simulated annealing schedule.

---

**Happy experimenting!**
