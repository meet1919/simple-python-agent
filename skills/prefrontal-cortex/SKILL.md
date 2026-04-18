---
name: prefrontal-cortex
description: >
  A structured reasoning framework for agents modeled on prefrontal cortex (PFC) function.
  Use this skill whenever an agent needs to solve multi-step problems, make decisions under
  uncertainty, plan across time, self-correct mid-task, use tools, or avoid impulsive/shallow
  responses. Triggers on: agentic tasks, tool use, complex reasoning, planning, debugging,
  tasks requiring inhibitory control ("don't just do X, think about whether X is right"),
  tasks where the agent has previously drifted or failed. This is the reasoning OS — apply
  it as the default scaffold for any non-trivial task.
allowed-tools: []
---

# Prefrontal Cortex (PFC) Reasoning Framework

A reasoning architecture for agents that mirrors the functional modules of the biological
prefrontal cortex. The PFC is the last brain region to fully develop (~age 25), and is
responsible for what separates deliberate human cognition from reactive animal behavior:
planning, inhibition, working memory, and meta-cognition.

This framework operationalizes those four modules as distinct reasoning layers an agent
must pass through before acting.

---

## The Four Modules

See `references/modules.md` for full detail on each module.
See `references/neuroscience.md` for the biological grounding.
See `references/failure-modes.md` for what goes wrong when each module is skipped.
See `references/translation-layers.md` for the meaning refinement mechanism (Hofstadter) and **Fluid De-Chunking**.
See `references/thinking-types.md` for cognitive frameworks like Divergent Expansion and First Principles.

### Module 1: Working Memory Maintenance (WMM)
*"What am I actually trying to do?"*

Hold the goal state actively in context. Check it has not drifted. Before any action, verify
current reasoning trace is still connected to the original intent.

**Core operation**: Goal anchoring + drift detection.

### Module 2: Inhibitory Control (IC)
*"Should I actually do this?"*

The most neglected module in LLM agents. Before executing an action — especially a tool call,
a commitment, or an irreversible step — pause and ask: is this the right action, or just the
first plausible action?

**Core operation**: Pre-action veto gate.

### Module 3: Temporal Integration (TI)
*"How does this moment connect to what came before and what comes next?"*

Connect past context (what was learned, decided, ruled out) to present action to future goal.
Avoid re-deriving what is already known. Carry forward conclusions with confidence weights.

**Core operation**: State accumulation + forward projection.

### Module 4: Meta-Cognition (MC)
*"Is my reasoning process working?"*

Monitor the quality of reasoning itself — not just the content. Flag when stuck in loops,
when confidence is mismatched to evidence, when a path has gone on too long without progress.

**Core operation**: Process monitoring + self-interruption trigger.

---

## The Reasoning Loop

Each reasoning step should pass through the modules in this order:

```
INCOMING TASK / OBSERVATION
         ↓
[WMM] — Goal check: Am I still solving the right problem?
         ↓
[TI]  — Context load: What do I already know that's relevant?
         ↓
[IC]  — Veto gate: Is my intended next action actually correct?
         ↓
[MC]  — Process check: Is my reasoning process itself healthy?
         ↓
ACT / RESPOND / CALL TOOL
         ↓
[MC]  — Post-action: Did outcome match expectation? Update priors.
```

This is not a linear pipeline run once — it is a **loop** run at each reasoning step.

---

## Trace Format

When generating reasoning traces for debugging or verification, use this structure:

```
TRACE_ID: <unique>
STEP: <n>

[WMM] Goal: <restate active goal>
      Drift detected: <yes/no — if yes, explain>
      Goal correction: <if drift, corrected goal>

[TI]  Prior context loaded: <what is already established>
      Confidence weights: <high/medium/low on each prior>
      Forward projection: <what this step should enable>

[IC]  Intended action: <what I am about to do>
      Veto check: <is this right? alternatives considered?>
      Decision: <proceed / veto / modify>

[MC]  Process quality: <is reasoning healthy?>
      Flags: <loop detected / confidence mismatch / path too long / none>
      Self-interrupt: <yes/no — if yes, reason>

ACTION: <what was done>
OUTCOME: <what resulted>
EXPECTATION MATCH: <yes/no/partial>
```

---

## Branching Traces

When a reasoning path splits, log explicitly:

```
BRANCH POINT at STEP <n>:
  Path A: <description> — estimated probability: <high/med/low>
  Path B: <description> — estimated probability: <high/med/low>
  Path C: <description> — estimated probability: <high/med/low>

SELECTED: Path <X>
REASON: <why this path, what the IC module flagged about others>
PATHS SUPPRESSED: <A, C — log why they were abandoned, not just which>
```

Suppressed paths are as important as selected ones for verifying the IC module's function.
They are where the IC module is most visible.

---

## Key Behavioral Principles

**1. Inhibition before action**
Never call a tool, make a commitment, or take an irreversible step without passing IC.
The first plausible action is not necessarily the right action.

**2. Goal anchoring**
At the start of each step, re-read the original task. Agents drift. WMM is the correction mechanism.

**3. Carry conclusions forward**
Do not re-derive what is already established. TI maintains a confidence-weighted state.
Revisiting settled questions is a process failure — MC should flag it.

**4. Log suppressions**
What you decided NOT to do is often more informative than what you did.
Suppressed paths must be logged with reasons.

**5. Meta-interrupt**
If MC flags a loop, a confidence mismatch, or excessive path length — stop.
Re-anchor to WMM before continuing. This is not a failure; it is the system working.

---

---

## What This Is Not

- **Not a chain-of-thought prompt** — CoT is a single linear trace. PFC is a multi-module loop.
- **Not a ReAct loop** — ReAct is Reason+Act alternation. PFC adds inhibition and meta-monitoring.
- **Not a planner** — planning is a subset of TI. This framework also governs moment-to-moment
  reasoning quality, not just task decomposition.
- **Not a personality** — this is a process architecture, not a persona or style guide.
