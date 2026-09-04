# Specialized Operators via a Multi-Objective Hyper-Heuristic

Source code for the paper:<br>
**Automatic Design of Specialized Variation Operators for the Multi-Objective Quadratic Assignment Problem** <br>
[GECCO, 2025]

> **[Authors]**<br>
> Adrián Isaí Morales-Paredes<br>
> Julio Juárez<br>
> Jesús Guillermo Falcón-Cardona<br>
> Hugo Terashima-Marín<br>
> Carlos A. Coello Coello<br>

A Grammatical-Evolution hyper-heuristic that generates variation operators
for multi-objective evolutionary algorithms (MOEAs), then benchmarks the
discovered operators against instances unseen during generation, on the
multi-objective Quadratic Assignment Problem (mQAP).

> **Note on reproducibility:** Running the commands below
> with the default (published) parameters reproduces the *methodology* and
> should land in the same range of operators, but will not reproduce the exact same
> discovered operators.

---

## Table of Contents

- [Background](#background)
- [Requirements](#requirements)
- [Installation](#installation)
- [Reproducing the experiments](#reproducing-the-experiments)
- [Repository structure](#repository-structure)
- [Data](#data)
- [Configuration reference](#configuration-reference)
- [Algorithms](#algorithms)
- [Output format](#output-format)

---

## Background

**Grammatical Evolution (GE)** evolves programs indirectly: an individual is
a *genome* (a list of integer codons), which is decoded into a *phenotype*
(here, a crossover-operator expression) by walking a BNF grammar and using
each codon, modulo the number of production choices, to pick the next
production rule. Two genomes that differ can decode to the same phenotype,
and small genome edits can produce structurally different phenotypes - this
indirection is what lets a standard genetic algorithm (selection, crossover,
mutation over integer genomes) search a space of *programs* and in this case
heuristics.

This repository uses GE to search a space of **variation (crossover) operators** for
permutation-encoded multi-objective evolutionary algorithms. Each candidate
operator is an expression built from primitives such as `move_right`,
`reverse`, `order_based(...)` (see [Algorithms](#algorithms)); a candidate is
scored by embedding it as the crossover operator inside an inner MOEA and
solving the **multi-objective Quadratic Assignment Problem (mQAP)**:

$$f_k(\pi) = \sum_{i} \sum_{j} w_k(i, j) \cdot d(\pi(i), \pi(j)), \quad k = 1, \dots, m$$

where $\pi$ is a permutation of facilities to locations, $w_k(i,j)$ is the
flow between facilities $i,j$ under objective $k$, and $d(\cdot,\cdot)$ is
the distance between locations. The goal is to find operators that help an
MOEA approximate the Pareto front of $(f_1, \dots, f_m)$ well, and that it
*generalize* on the problem, hence a strict split between instances seen
during generation and instances held out for evaluation.

- **`generation`**: the outer GE loop evolves a population of candidate
  operators (encoded as genomes), each scored by running an inner MOEA
  (MOEA/D, NSGA-II, or SMS-EMOA, via [pymoo](https://pymoo.org)) with that
  operator plugged in as crossover, on the training instances. Selection
  pressure favors operators with better hypervolume across instances.
- **`evaluation`**: takes the Best/Middle/Worst operators from a generation
  run and benchmarks them against held-out mQAP instances, alongside
  standard baseline operators (PMX, CX), across multiple MOEAs and multiple
  evaluation budgets (to see whether more generations meaningfully improves
  the discovered operators' performance).

---

## Requirements

- Python >= 3.10
- NumPy >= 2.0, pymoo >= 0.6.1, Matplotlib >= 3.9, pandas >= 2.3, tqdm >= 4.67

All dependencies are declared in `pyproject.toml` and installed automatically
by following the `Installation` steps. 

---

## Installation

```bash
# Clone the repository
git clone https://github.com/AdrianMP1/Generation-HyperHeuristic.git MOHH
cd MOHH
```

```bash
# Create and activate the environment
conda create -n mohh-dev python=3.12
conda activate mohh-dev
```

```bash
# Install the mohh package in editable mode
pip install -e .
```

Verify the installation:

```bash
python -c "import mohh; print('OK')"
```

---

## Running experiments

All commands must be run from the `MOHH/` directory. Three console commands
are installed by `pip install -e .`:

### Run the GE search

```bash
mohh-generate
```

Evolves candidate operators against the training instances in
`datasets/mqap/train/` and writes `results/Experiment_NNN/` (auto-numbered).
At the end, it extracts the Best/Middle/Worst operators from the final
generation and writes them to `<model>_operators.txt` in the experiment
folder, one file per `--models` entry.

### Benchmark a generation run

```bash
mohh-evaluate results/Experiment_001
```

Reads the operators produced by a `mohh-generate` run, benchmarks them
against the held-out instances in `datasets/mqap/test/`, alongside PMX/CX
baselines, across every solver in `--solvers` and every budget in
`--eval-budgets`, and writes CSVs, `.pof` front files, and box-plot figures
under `results/Experiment_001/evaluation_results/`.

### Both stages in one command

```bash
mohh-run --full
```

`--full` is a deliberate confirmation flag, since evaluation is by far the
more expensive stage - the command refuses to run without it.

### Overriding parameters

All three commands accept CLI overrides instead of editing `params.py` by
hand; anything not exposed as a flag can still be changed directly in
`generation/params.py` / `evaluation/params.py`. Run any command with `-h`
for the full flag list.

```bash
mohh-generate --models MOEAD --population-size 6 --generations 2 --elite-size 3 \
              --mo-population-size 10 --mo-generations 5

mohh-evaluate results/Experiment_001 --models MOEAD --solvers MOEAD,NSGAII \
              --mo-population-size 6 --mo-generations 4 --n-experiments 1 \
              --eval-budgets 10k:6,30k:18,50k:24
```

`mohh-evaluate` takes two related but distinct flags:

| Flag | Meaning | Default |
|------|---------|---------|
| `--models` | Which generation model(s)' operators to pull from `experiment_path` (reads `<model>_operators.txt`) | auto-detected from the experiment folder |
| `--solvers` | Which MOEA(s) to actually benchmark those operators with | `evaluation/params.py`'s `SOLVERS` (`MOEAD`, `NSGAII`, `SMSEMOA`) |

**Useful flags:**

| Flag | Effect |
|------|--------|
| `--models MOEAD,NSGAII,SMSEMOA` | Run generation's inner MOEA / pull evaluation operators for more than one model |
| `--solvers MOEAD,NSGAII` | Restrict which MOEAs evaluation benchmarks against |
| `--eval-budgets 10k:6,30k:18` | Comma-separated `label:evaluations` pairs; a budget unreachable at the configured `--mo-generations` is skipped rather than erroring |
| `--n-experiments N` | Repeated experiments per instance/operator combination |
| `--full` | Required on `mohh-run` to confirm running both stages |

### A quick, fast sanity run

To confirm the pipeline works end-to-end without waiting for a full-scale
run (the published-scale defaults - 50/30 generations, 105/300-500 MOEA
population/generations, 11 repeated experiments - can take a long time):

```bash
mohh-run --full --models MOEAD --population-size 8 --generations 2 \
         --elite-size 2 --mo-population-size 10 --mo-generations 3 \
         --n-experiments 3 --eval-budgets 10k:6
```

---

## Repository structure

```
MOHH/
├── pyproject.toml
├── README.md
├── grammars/
│   ├── naturals.bnf                 <- active grammar (permutation operators, used by default)
│   └── reals.bnf                    <- earlier real-valued grammar.
│                                        predates the project's focus on permutation-encoded
│                                        problems; not wired into any current entry point
├── datasets/
│   └── mqap/
│       ├── train/                   <- instances used during generation
│       └── test/                    <- held-out instances used during evaluation
│
├── results/                         <- created on first run; one Experiment_NNN/ per mohh-generate call
└── src/mohh/
    ├── cli.py                       <- mohh-generate / mohh-evaluate / mohh-run
    ├── main.py                      <- run_generation: orchestrates one or more generation models
    ├── run_evaluation.py            <- discover_models / extract_operators (reads *_operators.txt)
    ├── core/                        <- shared by both stages
    │   ├── params.py                <- Params singleton (dict-like global config)
    │   ├── representation/
    │   │   ├── grammar.py           <- BNF parser (adapted from PonyGE2)
    │   │   ├── mapper.py            <- genome -> phenotype mapping (adapted from PonyGE2)
    │   │   └── population.py        <- Population / Individual
    │   ├── problem/instance.py      <- QAP problem definition (pymoo Problem), Instance loader
    │   ├── operators/operator_template.py <- HH_Operator: wraps a decoded phenotype as a pymoo Crossover
    │   └── utilities/
    │       ├── algorithm/MO.py      <- non-dominated sorting, hypervolume, nadir point
    │       ├── algorithm/HH_functions.py <- grammar primitive functions (swap, reverse, order_based, ...)
    │       ├── instance_utils.py    <- lists train/ or test/ instance file paths
    │       ├── load_modules.py      <- string-name -> operator class dynamic dispatch
    │       ├── paths.py             <- project_root()
    │       └── print_utils.py       <- in-place CLI progress line updates
    │
    ├── generation/                  <- the GE search stage
    │   ├── params.py                <- generation defaults + set_params(experiment_path, model, overrides)
    │   ├── saver.py                 <- PopulationSaver / MyLogger singletons
    │   ├── algorithm/
    │   │   ├── hyperheuristic.py    <- HyperHeuristic: the outer GE loop (init, evaluate, evolve, replace)
    │   │   └── multiobjective.py    <- MOSolver: inner MOEA wrapper (MOEAD/NSGAII/SMSEMOA), per candidate
    │   ├── operators/                <- GE-level operators (on genomes)
    │   │   ├── initialization.py    <- Rvd: random valid population, discarding invalid/duplicate genomes
    │   │   ├── selection.py         <- Tournament
    │   │   ├── crossover.py         <- KPointCrossover, UniformCrossover
    │   │   └── mutation.py          <- BitFlipMutation
    │   ├── problem/instance.py      <- re-export shim over core.problem.instance
    │   ├── representation/population.py <- re-export shim + get_genome_usage()
    │   └── utilities/algorithm/HH_auxiliars.py <- compute_rank, test_individual (phenotype sanity eval)
    │
    └── evaluation/                   <- the benchmarking stage
        ├── params.py                <- evaluation defaults + set_params(overrides)
        ├── main.py                  <- execute_experiments: run_experiments() then make_figures()
        ├── experiment.py            <- run_experiments: the full sweep over instances x operators x solvers
        ├── algorithms.py            <- MOSolver (ABC), MOEA_Decomposition/NSGAII/SMS_MOEA, MyCallback
        ├── make_plots.py            <- reads saved CSVs, produces the box-plot figures
        ├── problem/instance.py      <- Instance subclass adding N-experiments initial-solution handling
        └── operators/
            ├── operator_template.py <- re-export shim over core.operators.operator_template
            ├── crossover.py         <- SBX_Cross, PMX_Cross, CX_Cross
            └── mutation.py          <- PM_Mutation, Swap_Mutation
```

**Two separate `MOSolver` classes exist by design**: `generation/algorithm/multiobjective.py::MOSolver`
dispatches on a `model_name` string and is built fresh per candidate operator (many short MOEA runs);
`evaluation/algorithms.py::MOSolver` is an `ABC` with one subclass per MOEA and adds eval-budget
snapshotting (`MyCallback`) for the benchmarking sweep. They share a name and a role but not a
contract, do not assume one's API from the other.

---

## Data

`datasets/mqap/{train,test}/` hold mQAP instances in the Knowles-Corne
(`KC`) benchmark format. Filename encodes the instance: `KC{n}-{k}fl-{tag}`,
e.g. `KC20-2fl-3rl` = 20 facilities, 2 flow matrices (objectives), variant
`3rl`. Each file starts with a header line, followed by the distance matrix
and one flow matrix per objective:

```
facilities= 20 objectives= 2 max_distances= ... max_flows= ... overlap= ... seed= ...
<N x N distance matrix>
<N x N flow matrix, objective 1>
<N x N flow matrix, objective 2>
...
```

Training instances (used only by `mohh-generate`) are smaller (`KC10`,
`KC20`, `KC30`); test instances (used only by `mohh-evaluate`) are held out
to check that discovered operators generalize rather than overfit the
training set.

---

## Configuration reference

Both `generation/params.py` and `evaluation/params.py` are plain Python
dicts merged into a `Params()` singleton at `set_params(...)` time, then
patched by any CLI overrides. Representative excerpts:

```python
# generation/params.py
hh_params = {
    'POPULATION_SIZE': 50,       # outer GE population
    'GENERATIONS': 30,           # outer GE generations
    'ELITE_SIZE': 15,            # kept unconditionally each generation

    'INITIALIZATION': "Rvd",
    'SELECTION': "Tournament", 'TOURNAMENT_SIZE': 3,
    'CROSSOVER': 'KPointCrossover', 'CROSSOVER_K_POINTS': 2, 'CROSSOVER_PARENTS': 2,
    'MUTATION': 'BitFlipMutation', 'MUTATION_PROBABILITY': 0.01,
}

mo_params = {
    'MO_MODEL': "MOEAD",         # inert default - overwritten by the CLI's --models value
    'MO_POPULATION_SIZE': 105,   # inner MOEA population, per candidate operator
    'MO_GENERATIONS': 300,
    'MO_MUTATION_BOOL': False,   # inner MOEA runs crossover-only by default
}
```

```python
# evaluation/params.py
mo_params = {
    'SOLVERS': ["MOEAD", "NSGAII", "SMSEMOA"],   # benchmarked by default
    'N_EXPERIMENTS': 11,                          # repeats per instance/operator/solver
    # 10500/31500/52500 = 105 (MO_POPULATION_SIZE) * 100/300/500 generations -
    # these are the published evaluation numbers.
    'EVAL_BUDGETS': {"10k": 10500, "30k": 31500, "50k": 52500},
    'MO_POPULATION_SIZE': 105,
    'MO_GENERATIONS': 500,
}
```

Both share `problem_params` (`PROBLEM_NAME: "QAP"`, `DATASET: "mqap"`,
`OPTIMIZATION_KIND: False` for minimization) and `grammar_params`
(`GRAMMAR_FILE: "naturals.bnf"`).

---

## Algorithms

### MOEAs (inner loop and benchmarking)

| Key | pymoo class | Used in |
|-----|-------------|---------|
| `MOEAD` | `pymoo.algorithms.moo.moead.MOEAD` | generation (inner loop, default) and evaluation |
| `NSGAII` | `pymoo.algorithms.moo.nsga2.NSGA2` | generation and evaluation |
| `SMSEMOA` | `pymoo.algorithms.moo.sms.SMSEMOA` | generation and evaluation |

### Grammar primitives (`grammars/naturals.bnf`)

The active grammar builds operator expressions from these primitives
(implemented in `core/utilities/algorithm/HH_functions.py`):

| Primitive | Arity | Description |
|-----------|-------|-------------|
| `move_right` | 1 | Rotate the permutation one position to the right |
| `reverse` | 1 | Reverse the permutation |
| `map_list` | 2 | Use each list as an index permutation of the other |
| `alternate_elements` | 2 | Interleave elements from both parents, then de-duplicate |
| `order_based(fill, preserve, x, y)` | 2 | `preserve` selects elements/segments to keep from `x`, `fill_first_occurring` fills the rest with the first not-yet-used value from `y`, in order |
| `preserve_elements` / `preserve_segments` | - | Two selection strategies for `order_based`'s `preserve` slot |

`grammars/reals.bnf` additionally defines real-valued primitives
(`sin`, `cos`, `convolution`, `one_point`, `masked_cross`, ...) but is not
wired into any current entry point.

**The grammar can be extended and modified once its non-terminals are programmed accordingly**

---

## Output format

After `mohh-generate`, then `mohh-evaluate <path>`, the results tree is:

```
results/Experiment_NNN/
├── <MODEL>_operators.txt                     <- "Best: <phenotype>\nMiddle: ...\nWorst: ..."
├── <MODEL>_<hostname>_<timestamp>/
│   └── generation_results/
│       ├── parameters.txt                    <- every param value used for this run
│       ├── CLI_output.log
│       ├── individuals/
│       │   └── Individual_NNNNNN/
│       │       ├── general_info.json         <- name, phenotype, nodes, depth, genome, codons_usage
│       │       └── instance_<name>.json      <- per-instance pareto set/front/solutions for this individual
│       ├── generations/
│       │   └── generation_NNNN/
│       │       ├── population.json           <- individual IDs in this generation
│       │       ├── offspring.json            <- (only present when offspring were just created)
│       │       └── Instance_Fronts_<name>.json <- per-instance consolidated non-dominated fronts
│       └── initial_solutions/permutation/<instance>.txt
│
└── evaluation_results/
    ├── initial_solutions/{permutation,real}/<instance>/{seeds.txt, experiment_NNN.txt}
    └── <SOLVER>/<budget>/
        ├── <instance>.csv                    <- one row per experiment, one column per operator x mutation
        ├── fronts/<instance>/
        │   ├── <label>_<mutation>_<solver>.pof[,_norm.pof]   <- median front per operator combination
        │   └── best_front_consolidated[_norm].pof
        └── Figures/{NoMutation,WithMutation}/<instance>_{NM,WM}.png
```

**`<instance>.csv` columns** are named `<label>_<combination>_<NM|WM>_<solver>`
(e.g. `MOEAD_Best_NM_MOEAD`, `None_PMX_WM_NSGAII`), where `label` is `MOEAD`
(the generation model) for discovered operators or `None` for baselines,
`combination` is `Best`/`Middle`/`Worst`/`Standard`/`PMX`/`CX`, and each row
is one repeated experiment's hypervolume.

A budget directory is only created if at least one solver/instance actually
reached it; if `--mo-generations` is too small for a given `--eval-budgets`
entry, that budget is silently skipped for that run rather than erroring.
