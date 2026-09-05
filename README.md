# Program Synthesis by Reinforcement Learning over Abstract Syntax Trees

An experiment aimed at [ARC-AGI-2](https://arcprize.org/): instead of training a network to
*predict* the output grid of a puzzle, train an agent to **write a small program** that produces it.

> **Status: research prototype with a negative result.** The full pipeline — DSL, sandboxed
> interpreter, AST↔graph encoding, RL action space, two agent architectures, training
> instrumentation — is built and tested. The agent does **not** yet solve tasks. The
> [Results](#results) section reports what actually happened and why, rather than a
> success story. The repo is here as an example of the engineering and the experimental
> method, not as a leaderboard entry.

---

## The idea

ARC-AGI-2 puzzles are input/output grid pairs. The transformation rule behind a puzzle is
usually short and procedural — *"invert every pixel"*, *"extend each line to the border"*,
*"recolour the largest shape"*. A neural net asked to emit the output grid directly has to
re-derive that rule inside its activations for every cell it draws.

The hypothesis here is the opposite framing:

> The rule *is* a program. Learn to search program space, not pixel space.

That buys three things a pixel-space model does not get for free:

- **Verifiable.** A candidate program either reproduces the training pair or it does not.
  There is no partial-credit hallucination — you run it.
- **Compositional.** `while` inside `if` inside `while` generalises to grid sizes the model
  never saw. A pixel decoder does not.
- **Legible.** The output is a readable AST, so a failure can be inspected.

The hard part is the search. Program space is discrete, combinatorial, and mostly full of
programs that crash. The approach taken here: **make the search itself a reinforcement
learning problem over graphs**. The state is the partially-written program as an AST; an
action is one legal edit to that AST; the reward is how close running the program gets you
to the target grid.

---

## How it works

```
                  ┌──────────────────────────────────────────────────────┐
                  │                                                      │
                  ▼                                                      │
   ┌──────────────────────────┐                                          │
   │ Codeblock (partial AST)  │                                          │
   └────────────┬─────────────┘                                          │
                │ to_ast()                                               │
                ▼                                                        │
   ┌──────────────────────────┐      ┌───────────────────────────────┐   │
   │ networkx DiGraph         │─────▶│ GNN encoder → state embedding │   │
   │ (typed, ordered edges)   │      └───────────────┬───────────────┘   │
   └────────────┬─────────────┘                      │                   │
                │ get_action_space()                 ▼                   │
                ▼                          ┌──────────────────┐          │
   ┌──────────────────────────┐            │ policy scores    │          │
   │ legal edits:             │───────────▶│ every legal edit │          │
   │ (parent, node_type,      │            └────────┬─────────┘          │
   │  insertion order)        │                     │ argmax / sample    │
   └──────────────────────────┘                     ▼                    │
                                          ┌──────────────────┐           │
                                          │ new_node(...)    │───────────┘
                                          └────────┬─────────┘
                                                   │
                                                   ▼
                              ┌──────────────────────────────────────┐
                              │ sandboxed interpreter runs the       │
                              │ program → OUTPUT_ENV                 │
                              │ reward = closeness to expected grid  │
                              └──────────────────────────────────────┘
```

### 1. A minimal instruction language

[`instruction_language/`](instruction_language/) is a hand-built DSL whose entire point is to be
*small enough for an agent to search* while still being Turing-adjacent. Fifteen node types
([`elements/types.py`](instruction_language/elements/types.py)):

| Group        | Nodes                                                         |
| ------------ | ------------------------------------------------------------- |
| Structure    | `codeblock`, `term`, `constant`, `none_type`                  |
| Memory       | `read_var`, `write_var`                                       |
| Grid I/O     | `read_pixel_input`, `read_pixel_output`, `write_pixel_output` |
| Comparison   | `equal_to`, `greater_than`, `less_than`                       |
| Arithmetic   | `sum`                                                         |
| Control flow | `if`, `while`                                                 |

Every node implements the same [`Executable`](instruction_language/elements/base.py) interface —
`execute()`, `add_child()`, `delete_child()`, `to_ast()` — so the tree is simultaneously an
interpretable program and a graph the agent can edit. That single interface is what makes the
rest of the system possible: the agent never manipulates source text, only typed tree nodes.

A worked example lives in [`tests/pytest_setup.py`](tests/pytest_setup.py): a hand-written program
that inverts every pixel of the input grid, built from nested `while` loops, an `if`, and
variable arithmetic. It doubles as the fixture the test suite executes.

### 2. A runtime the agent cannot break

Agent-written programs are hostile by default — infinite loops, unbound reads, type errors on
almost every step. [`surroundings/`](instruction_language/surroundings/) contains the containment:

- **`Environment`** — a sparse `(x, y) → value` grid with `from_list` / `to_list` conversion, and
  an `evaluate()` that counts cell-wise mismatches between two grids.
- **`GEMService`** (Global Environment Manager) — a registry of named grids: `INITIAL_ENV`
  (the puzzle input), `OUTPUT_ENV` (the agent's canvas), `EXP_OUTPUT_ENV` (the target).
  Instruction nodes reference grids by fixed key, so the agent cannot invent a grid handle.
- **`MemoryManager`** — a namespaced variable store with a stack of scopes, so a `codeblock`
  entered inside a loop gets its own frame and reads fall through to enclosing scopes.
- **`GISManager`** (Global Interpreter Settings) — caps enforced at runtime: `max_loop_iterations`
  (2500) and `max_run_time_seconds` (30), plus an interpreter lock so two runs cannot interleave
  global state.
- **`InstructionInterpreter`** — executes a program on a worker thread with a hard wall-clock
  timeout and resets memory afterwards, so a non-terminating candidate costs one timeout rather
  than the training run.

### 3. Programs as graphs

`to_ast()` walks the tree into a `networkx.DiGraph` where each node carries its type index and a
`carrying_value` (the literal a `constant` holds, or the address a `read_var` targets), and each
edge carries an `order` attribute — because in a program, argument position is meaning:
`less_than(a, b)` is not `less_than(b, a)`.

[`ast_transformer.py`](instruction_language/ast_transformer.py) then one-hot encodes the node type,
appends the carrying value (with a sentinel `999` for "unset"), and hands the graph to
`torch_geometric.utils.from_networkx`. It also contains `hierarchy_plot`, a left-to-right tree
layout used to eyeball what the agent actually wrote.

### 4. The code writer: program editing as an action space

[`code_writer.py`](code_writer.py) is the bridge between "program" and "RL environment", and it is
where most of the design work sits.

`get_action_space(codeblock)` traverses the current AST and enumerates **every structurally legal
edit** as a `(parent_node, node_type, insertion_order)` triple. The rules are per node type: a
`codeblock` accepts any non-`none` node appended to its execution plan; a `while` accepts a
condition and a body; a `write_pixel_output` accepts exactly three `term` children (value, x, y);
a `constant` accepts nothing. This is the project's main trick — **illegal programs are never
representable**, so the agent spends its search budget on semantics rather than on rediscovering
syntax.

`new_node(...)` materialises the chosen edit; `evaluate(...)` runs the resulting program and
scores it:

```python
deviation      = mismatching_cells(OUTPUT_ENV, EXP_OUTPUT_ENV)
deviation      = deviation ** 2          # penalise large misses superlinearly
reward         = max(0, 100 - deviation) / 100
```

Crashes and timeouts return `0.0`, with a `skip_episode` flag so a timeout aborts the episode
instead of burning 30 more steps at 30 s each.

### 5. Two agent architectures

**v1 — GCN + learned action scorer** ([`new_main.py`](new_main.py)). Two `GCNConv` layers with
mean pooling produce a 64-d state embedding; an MLP embeds each candidate action into 32-d; a
scorer MLP reads `(state, action)` and predicts the reward. Action selection is ε-greedy
(`rely_on_model_weight = 0.7`), and the scorer is regressed on the observed immediate reward with
MSE — effectively a contextual bandit over edits. A separate head predicts the literal
`carrying_value` when the chosen node needs one. Includes checkpointing every 100 episodes and
resumable training via `--checkpoint`.

**v2 — Graph Attention + PPO** ([`rl_agent/main.py`](rl_agent/main.py)). Replaces the GCN with a
4-head `GATConv` encoder (attention lets a node weigh its children by relevance rather than
averaging them), and replaces the bandit objective with actor-critic PPO: a policy head over the
action set, a value head on the state, discounted returns, advantage-weighted policy loss, and
updates batched over 8 episodes. Exploration decays from ε = 0.5 to 0.05 over training.

---

## Results

Training telemetry for every run is committed under [`reporting/data_repo/`](reporting/data_repo/)
and analysed in the notebooks in [`reporting/`](reporting/). Headline: **the agent never solved
the target grid.** No run in the archive reached reward `1.0`.

| Run               | Agent  | Episodes | Mean reward | Non-zero-reward rate (first → last decile) |
| ----------------- | ------ | -------- | ----------- | ------------------------------------------ |
| `20250814_054526` | v1 GCN | 100,020  | 0.097       | 0.09 → 0.11                                |
| `20250822_095524` | v1 GCN | 11,001   | 0.136       | 0.22 → 0.22                                |
| `20250829_185550` | v2 PPO | 100,000  | 0.000       | 0.00 → 0.00                                |
| `20250914_213640` | v2 PPO | 100,000  | 0.000       | 0.00 → 0.00                                |

Three things the data actually says:

**1. The reward signal is bimodal, and the plateau is a trap.** In the later v1 runs, episode
reward takes exactly two values: `0.0` and `0.64`. The `0.64` is not partial progress — it is
what you score by writing *nothing at all* to the output grid (6 mismatched cells → `(100 − 36)/100`).
So the reward landscape rewards "produce a program that runs" and gives no gradient toward
"produce a program that draws the right pixels". A shaped, per-cell-progress reward is the first
thing that needs to change.

**2. The PPO agent's flat zero is a bug, not a training failure.** `rl_agent/main.py` never calls
`GEMService.add_env("EXP_OUTPUT_ENV")` — the registration that `new_main.py` does at startup.
Every call into `code_writer.evaluate` therefore raises `ValueError: Environment 'EXP_OUTPUT_ENV'
does not exist`, which the broad `except Exception` swallows and converts into `reward = 0.0`.
Three runs totalling ~7.5 hours of compute optimised against an identically-zero signal. The
broad exception handler that made training robust to agent-written crashes also hid a harness
crash — a lesson worth more than the compute it cost.

**3. The engineering instrumentation did its job.** Two real problems were found and fixed by the
telemetry rather than by guesswork:

- *A memory leak in the interpreter's namespace registry.* The 100k-episode run climbed from
  370 MB to 1,087 MB RSS, peaking at 2,122 MB. After the `MemoryManager` rework, the 11k-episode
  run stayed flat at 360 → 345 MB (peak 440 MB).
- *Per-step cost growing with program size.* Profiling the loop into four phases —
  action-space construction, action selection, execution, optimisation — showed
  ([`reporting/screenshots/`](reporting/screenshots/)) that graph re-encoding, not the neural
  network and not program execution, dominates and grows linearly as the AST does. Mean episode
  time rose from 0.30 s to 1.45 s across a single run for that reason. Incremental re-encoding of
  the changed subtree is the obvious fix.

The test suite (13 tests, all passing) covers AST conversion, program execution, the action
space, node creation/deletion, memory scoping, interpreter locking, and the loop-iteration cap.

---

## Repository layout

```
instruction_language/        the DSL
├── elements/                node types: base, instructions, conditions,
│                            operators, control_statements, types
├── surroundings/            Environment/GEMService, MemoryManager, GISManager
├── interpreter.py           sandboxed execution with wall-clock timeout
└── ast_transformer.py       AST → PyTorch Geometric encoding, tree plotting

code_writer.py               action space, node creation, reward function
new_main.py                  v1 agent: GCN + action scorer  (main training entry point)
rl_agent/main.py             v2 agent: Graph Attention + PPO

tests/                       pytest suite (13 tests)
reporting/                   training telemetry + analysis notebooks
editor/                      tkinter tool for drawing input/output grid pairs by hand
docker/                      ROCm PyTorch image used for GPU runs

nn.py, nn_new_architecture.py, molecular_exa.py, main.py,
plot_test.py, loss_test.py, memory_test.py
                             exploratory scratch files kept for provenance;
                             not part of the pipeline
```

## Notes on scope

This was a solo side project built to explore whether learned program synthesis is a tractable
attack on ARC-AGI-2. It is not a competition submission and does not read the ARC task files yet.
What it does demonstrate is the full loop — a DSL, a sandboxed interpreter, a graph encoding, a
legality-constrained action space, two RL agents, and enough instrumentation to diagnose its own
failures — and an honest account of where that loop breaks.
