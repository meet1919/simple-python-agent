# Contributing to Simple Python Agent

Thank you for your interest in contributing to this experimental research project!

## How to Contribute

This is a dynamic, high-velocity research repository focused on autonomous agent tooling, specifically evaluating logical reasoning capabilities (Prefrontal Cortex) on public benchmarks (SWE-Bench, WebArena, GSM8K).

### Adding New Skills

We welcome pull requests for new isolated agent skills!
To submit a new skill:
1. Create a directory in `/skills/[your-skill-name]`
2. Add a `SKILL.md` file wrapped in YAML frontmatter exactly like the existing skills.
3. Wire up any tools required for your skill inside `core/tools.py`. Keep standard Python dependencies to an absolute minimum to maintain framework speed.

### Bug Fixes

If you discover critical bugs in the context-sliding or looping architecture, please open an issue first with a screenshot of the traceback or token overflow before submitting a PR.

### License

By contributing to this repository, you agree to license your contributions under the MIT License included at the root of this project.
