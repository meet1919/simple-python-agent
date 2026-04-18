# Security Policy

## Supported Versions

This is an **experimental research project** designed to act as an unconstrained, highly autonomous AI Agent. It is not currently recommended for production workloads.

## Experimental Hazards

This framework provides the LLM (Large Language Model) with **direct, interactive access to your local physical OS** via tools like `run_bash_command` and `edit_file`.

The models governing this framework (like GPT-4-class models) can and will autonomously generate and execute complex, multi-stage terminal operations. **Running this agent on a system with highly sensitive data or production-critical state is not advised.**

### Best Practices

- **Sandbox Environment:** ALWAYS run this agent in an isolated environment (e.g., Docker container, Virtual Machine) if you expand the agent's autonomous limits.
- **Human-In-The-Loop (HITL):** Keep the builtin `Confirm` prompts enabled in `core/tools.py`. Do not bypass them unless the run is strictly sandboxed.
- **Tool Tracing:** Monitor output closely. 

## Reporting a Vulnerability

If you've noticed abnormal prompt injection vulnerabilities or accidental systemic execution behaviors during agent testing, please report it via a GitHub issue directly rather than via email. We track all agent-escape payloads openly so the community can patch prompt architectures.
