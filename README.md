# Simple Python Agent

This is a minimal, framework-free Python agent built on top of the OpenAI API. It implements a skill routing mechanism, context sliding-window/compaction, and dynamic tool dispatch.

## Features
- **Skill Router**: Automatically routes user requests to the appropriate skill based on chat history and intent.
- **Context Compaction**: Uses a cheaper model to summarize older messages and maintain context without blowing up the token budget.
- **Skill System**: Defines skills simply via a `SKILL.md` file featuring YAML frontmatter for metadata (allowed tools, names) and markdown for instructions.
- **Tool Dispatch**: Safely validates and executes python functions acting as tools.

## Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your OpenAI API key.

## Creating a Skill
Create a new folder in the `skills` directory and add a `SKILL.md` file using the following format:

```markdown
---
name: video-editing
description: Use when the user wants to manipulate existing media.
allowed-tools: [transcribe_audio, mix_audio_tracks]
---

Your job: You are a video editor...
```

## Running the Agent
Run the interactive CLI:
```bash
python cli.py
```
