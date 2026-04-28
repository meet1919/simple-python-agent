# Simple Python Agent


This is a minimal, framework-free Python agent built on top of the OpenAI API. It implements an OpenClaw-inspired dynamic JIT skill architecture, context sliding-window/compaction, and tool dispatch.

## Features

- **Procedural Memory & Myelinated Agents**  
  Stores successful solution traces based on task structural signatures. When the agent recognizes structurally identical tasks, it *"myelinates"* the pathway by recalling and injecting the previously established successful solution trace into the prompt to shortcut reasoning, reduce token usage, and improve reliability.

- **LLM Wiki Maintainer**  
  The agent can incrementally build and maintain a persistent personal knowledge base composed of interlinked markdown files. It can ingest new sources, intelligently query the wiki, and run lint passes to check for contradictions and dead links.

- **JIT Skill Architecture (OpenClaw-Inspired)**  
  Replaces static pre-routing with dynamic Just-In-Time skill loading. The agent receives an XML menu of available skills in its system prompt and fetches full instructions on-demand via a `read_skill_documentation` tool.

- **Dynamic Tool Binding**  
  Prevents "tool bloat" by strictly scoping tool access. The agent is initialized with minimal global tools. When a skill is loaded, the agent dynamically binds only the tools specified in that skill's `allowed-tools` array, replacing any previously bound tools.

- **Autonomous Skill Creation**  
  Includes a native `skill-creator` allowing the agent to securely write, evaluate, and inject completely new skills and python tools into `self_authored` directories on the fly.

- **Prefrontal Cortex (PFC) Subagent**  
  Optional middleware that triggers automatically during JIT skill loading for complex tasks. It uses biological reasoning frameworks (WMM, IC, TI, MC) to de-chunk raw input, identify ambiguities, and inject cognitive preprocessing before the full skill executes.

- **Post-Action Reflection**  
  Skills can utilize a built-in `reflect` tool to evaluate tool outcomes directly against the active goal.

- **Context Compaction**  
  Uses a cheaper model to summarize older messages and maintain context without blowing up the token budget.

- **Skill System**  
  Defines skills simply via a `SKILL.md` file featuring YAML frontmatter for metadata (allowed tools, names, and subagent flags) and markdown for instructions.

- **Tool Dispatch**  
  Safely validates and executes python functions acting as tools.

## ⚠️ Security Warning

**This is a highly experimental, physical agent framework.**
Skills mapped to local executors (like `run_bash_command`) give the AI direct control over the host system. The framework uses a human-in-the-loop (HITL) prompt loop for shell executions by default, but it is highly recommended to run this framework inside a Docker container or VM during extended autonomous tests. Please read `SECURITY.md` for more information.

## Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your OpenAI API key.

## Creating a Skill
Create a new folder in the `skills` directory and add a `SKILL.md` file using the following format. Add `requires-pfc: true` to route complicated reasoning requests through the subagent.

```markdown
---
name: swe-bench
description: Use when the user asks you to resolve software issues, navigate a codebase, fix bugs, or run tests. Perfect for evaluating autonomous programming capabilities.
allowed-tools: [view_file, edit_file, run_bash_command, reflect]
requires-pfc: true
---

Your job: You are an autonomous software engineering research agent...
```

## Running the Agent
Run the interactive CLI:
```bash
python cli.py
```

## Usage Guide

Once the interactive CLI is running, you can communicate with the agent using natural language. The agent dynamically loads skills based on your request.

### 1. General Queries & OS Control
- You can ask the agent to explore your filesystem, write scripts, or execute commands.
- Example: *"What's in my current directory?"* or *"Write a python script that prints 'Hello World' and run it."*
- **Note:** Any bash command or python execution will prompt you for human-in-the-loop approval [Y/n] before running.

### 2. Using the LLM Wiki
To test the newly added LLM Wiki skill:
1. Create a text file with some information (e.g., `test_source.md`).
2. Ask the agent: *"Please ingest test_source.md into my wiki."*
3. The agent will JIT load the `llm-wiki-maintainer` skill, run the PFC cognitive middleware to understand your intent, and create an `index.md`, `log.md`, and summaries.
4. You can then query your wiki: *"What did I save in my wiki recently?"*

### 3. Testing Procedural Memory (Myelination)
The agent automatically records successful tool traces for tasks it performs. To see it in action:
1. Ask the agent to perform a task that triggers a complex skill (like ingesting a file into the wiki).
2. After it successfully finishes, the agent will print `Stored solution trace in procedural memory.`
3. Ask the agent to perform a *structurally identical task* (e.g., *"Ingest another_file.md into the wiki"*).
4. The agent's Prefrontal Cortex will recognize the task signature and print `Procedural Memory Match Found! Injecting myelinated pathway...` in yellow, signaling it is bypassing standard reasoning to execute the proven trace efficiently.
