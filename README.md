# MOHH — Multi-Objective Hyper-Heuristic

A Grammatical-Evolution hyper-heuristic that generates variation operators
for multi-objective evolutionary algorithms (MOEAs), then benchmarks the
discovered operators against instances unseen during generation.

- `generation`: evolves a population of candidate operators, encoded as GE
  genomes and decoded via a BNF grammar into phenotype expressions, scored
  by embedding each candidate as a crossover operator inside a MOEA
  (currently MOEA/D, via [pymoo](https://pymoo.org)) solving the mQAP.
- `evaluation`: takes the Best/Middle/Worst operators from a generation run
  and benchmarks them against held-out mQAP instances, alongside standard
  baseline operators (PMX, CX), across several MOEA/D generation budgets.

## Installation

```bash
conda create -n mohh-dev python=3.12
conda activate mohh-dev
pip install -e .
```

Requires Python 3.10+. `pymoo` needs a compiled wheel for your platform;
this has been validated on Python 3.9 (pymoo 0.6.1.5) and 3.12 (pymoo 0.6.2).

## Usage

Three console commands, installed by `pip install -e .`:

```bash
# Run the GE search, writing results/Experiment_NNN/
mohh-generate

# Benchmark the operators from a generation run against test instances
mohh-evaluate results/Experiment_001

# Generation followed by evaluation in one go (--full is a deliberate
# confirmation, since evaluation is by far the more expensive stage)
mohh-run --full
```

All three accept overrides instead of editing `params.py` by hand:

```bash
mohh-generate --population-size 6 --generations 2 --elite-size 3 \
              --mo-population-size 10 --mo-generations 5

mohh-evaluate results/Experiment_001 --mo-population-size 6 \
              --mo-generations 4 --n-experiments 1 \
              --eval-budgets 10k:6,30k:18,50k:24
```

Run any command with `-h` for the full flag list. Anything not exposed as a
flag can still be changed directly in `generation/params.py` /
`evaluation/params.py`.

### Evaluation budgets

Evaluation snapshots each MOEA/D run's Pareto front at three points, labeled
by total evaluation count (`EVAL_BUDGETS` in `evaluation/params.py`):
by default `10k`/`30k`/`50k` evaluations (105 × 100/300/500 generations —
these are the published reference points). This is what lets the resulting
plots show whether more generations meaningfully improves the discovered
operators. If `MO_GENERATIONS` is set too low to reach a given budget for a
smaller/test run, that budget is skipped rather than producing an error.

## Project layout

```
src/mohh/
  core/         shared code: grammar/GE representation, QAP problem
                definition, Params singleton, MOEA utilities
  generation/   the GE search stage
  evaluation/   the benchmarking stage
  cli.py        mohh-generate / mohh-evaluate / mohh-run
grammars/
  naturals.bnf  active grammar (permutation operators, used by default)
  original.bnf  earlier real-valued grammar, kept for provenance -
                predates the project's focus on permutation-encoded
                problems; not wired into any current entry point
datasets/mqap/  mQAP instances (train/test/temporal)
```
