# ToolFence

> **Task-Scoped Security for AI Coding Agents**  
> **Bob reasons. ToolFence enforces.**

ToolFence is a security gateway for AI coding agents that enforces **least-privilege, task-scoped access** to developer tools.

Instead of giving an AI agent broad access to repositories, CI, tickets, deployments, and secrets, ToolFence lets the agent propose the **minimum capabilities required for one task**. A trusted developer-defined approval ceiling is kept separate from the model, and every protected action is deterministically evaluated before execution.

Built for the **IBM Bob 2.0 Hackathon**.

---

## Why ToolFence?

AI coding agents are becoming increasingly capable, but their tool access is often too broad.

A typical agent may have access to:

- source repositories
- issue trackers
- CI pipelines
- pull requests
- deployment systems
- secrets
- production environments

The problem is simple:

> An agent may only need a few actions to complete a task, but it can often see and use far more.

ToolFence reduces that attack surface by turning a natural-language task into a **task-specific capability boundary**.

---

## Core Idea

```text
Developer Task
      ↓
IBM Bob
      ↓
Minimum Capability Proposal
      ↓
ToolFence
 ┌─────────────────────────────┐
 │ Trusted Task Context        │
 │ Developer Approval Ceiling  │
 │ Policy Compiler             │
 │ Deterministic Evaluator     │
 │ Protected Dispatcher        │
 │ Audit Log                   │
 └─────────────────────────────┘
      ↓
Protected MCP Tools
      ↓
Tickets / Repo / CI / PR / Release / Secrets
```

### Security principle

```text
Bob reasons.
ToolFence enforces.
```

IBM Bob can reason about what permissions are required.

ToolFence decides whether those permissions and subsequent tool calls are allowed.

---

## What ToolFence Protects

ToolFence currently exposes **11 protected capabilities**:

| Service | Capability |
|---|---|
| Ticket | `ticket.get` |
| Ticket | `ticket.comment` |
| Ticket | `ticket.delete` |
| Repository | `repo.read` |
| Repository | `repo.write` |
| Pull Request | `pull_request.create` |
| CI | `ci.run` |
| CI | `ci.status` |
| Release | `release.status` |
| Release | `release.deploy` |
| Secrets | `secret.read` |

The MCP server also exposes four control-plane tools:

- `toolfence.list_capabilities`
- `toolfence.task_context`
- `toolfence.propose_policy`
- `toolfence.policy_status`

That gives the current MCP server **15 tools total**.

---

## Trust Model

ToolFence separates three different concepts.

### 1. Canonical task context

The agent can safely retrieve the task identity:

```json
{
  "task_id": "BUG-17-FIX",
  "task": "Fix BUG-17, run CI, and create a pull request."
}
```

The task context does **not** reveal the trusted approval ceiling.

### 2. Agent capability proposal

Bob determines the minimum access required and submits a capability proposal.

Example:

```json
{
  "task": "Fix BUG-17, run CI, and create a pull request.",
  "allowed": [
    { "tool": "ticket.get", "resource": "BUG-17" },
    { "tool": "repo.read", "resource": "project/*" },
    { "tool": "repo.write", "resource": "project/src/*" },
    { "tool": "ci.run", "resource": "feature/BUG-17" },
    { "tool": "ci.status", "resource": "feature/BUG-17" },
    { "tool": "pull_request.create", "resource": "feature/BUG-17" }
  ]
}
```

### 3. Trusted developer approval ceiling

A separately trusted approval defines the maximum authority the task may receive.

Bob cannot supply this ceiling.

ToolFence validates the proposal against it before activating a policy.

---

## Fail-Closed Behavior

ToolFence is designed to fail closed.

```text
No active policy
→ DENY

Tool not granted
→ DENY

Resource outside approved scope
→ DENY

Malformed arguments
→ DENY

Unknown capability
→ DENY
```

A denied action is not forwarded to the protected backend.

---

## Golden Demo

The demo task is:

```text
Fix BUG-17, run CI, and create a pull request.
```

### Approved task policy

The active golden policy grants six capabilities:

| Tool | Resource |
|---|---|
| `ticket.get` | `BUG-17` |
| `repo.read` | `project/*` |
| `repo.write` | `project/src/*` |
| `ci.run` | `feature/BUG-17` |
| `ci.status` | `feature/BUG-17` |
| `pull_request.create` | `feature/BUG-17` |

Sensitive or unnecessary capabilities remain outside the task policy, including:

- `ticket.comment`
- `ticket.delete`
- `release.status`
- `release.deploy`
- `secret.read`

---

## Real Denial Demonstration

A live IBM Bob run attempted:

```text
secret.read
resource: production-key
```

ToolFence returned:

```json
{
  "decision": "DENY",
  "reason_code": "TOOL_NOT_GRANTED",
  "execution_status": "NOT_EXECUTED",
  "result": null
}
```

This demonstrates that a capability can be visible to the agent while remaining unavailable to the active task policy.

The secret backend was not executed.

---

## Real End-to-End Execution

The golden task was successfully completed through ToolFence:

```text
ticket.get
    ↓
repo.read
    ↓
repo.write
    ↓
ci.run
    ↓
ci.status
    ↓
pull_request.create
```

### BUG-17

The bug was:

```python
def calculate_total(prices):
    return sum(prices[1:])
```

The slice skipped the first cart item.

The fix was:

```python
def calculate_total(prices):
    return sum(prices)
```

### CI result

The protected CI service verified:

| Check | Input | Expected | Result |
|---|---|---:|---:|
| `multiple_items` | `[10, 20, 30]` | `60` | `60` |
| `empty_cart` | `[]` | `0` | `0` |
| `single_item` | `[25]` | `25` | `25` |

Final CI status:

```text
PASSED
```

A pull request was then created on:

```text
feature/BUG-17
```

---

## Audit Trail

Every protected ToolFence action records an audit event.

An audit event captures:

- task ID
- tool
- resource
- ALLOW / DENY decision
- reason code
- matched policy scope
- policy ID
- backend execution status
- backend error metadata when applicable
- audit event ID

ToolFence deliberately avoids storing unnecessary backend payloads such as secret values or file contents in the audit log.

Audit storage:

```text
runtime/audit.jsonl
```

---

## Benchmark

ToolFence includes a deterministic authorization replay benchmark.

The benchmark contains **16 predefined scenarios** across:

- legitimate actions
- forbidden actions
- resource-boundary cases

Run it with:

```powershell
.\.venv\Scripts\python.exe -m benchmark.run_benchmark
```

### Measured result

```text
Cases matched: 16/16
Ground-truth match rate: 100.00%
Forbidden action blocking rate: 100.00%
False denial rate: 0.00%
Boundary case accuracy: 100.00%
Privilege reduction ratio: 45.45%
Mean authorization evaluation: 0.0205 ms
Max authorization evaluation: 0.0525 ms
```

The latency values above are **authorization policy-evaluation time**, not end-to-end IBM Bob or MCP latency.

### Privilege reduction

The demo capability inventory contains:

```text
11 available protected capabilities
6 granted capabilities
```

Therefore:

```text
1 - (6 / 11) = 45.45%
```

ToolFence reduces the active task capability surface by **45.45%** in the golden scenario.

---

## IBM Bob Integration

ToolFence runs as a real MCP STDIO server and integrates directly with IBM Bob.

Project configuration:

```text
.bob/mcp.json
```

Entrypoint:

```text
app/mcp_stdio.py
```

Bob can:

1. read canonical task context
2. inspect the capability inventory
3. reason about the minimum required permissions
4. submit one complete task capability proposal
5. verify the policy is active
6. execute protected actions through ToolFence

---

## Bob Skill

The repository includes a project skill:

```text
.bob/skills/compile-task-policy/SKILL.md
```

The skill teaches Bob to follow the secure ToolFence workflow:

```text
task_context
      ↓
list_capabilities
      ↓
reason about minimum authority
      ↓
propose_policy exactly once
      ↓
policy_status
      ↓
protected execution
```

The skill explicitly instructs Bob not to:

- inspect `config/golden_task.json`
- use `execute_command` to discover trusted approval limits
- probe `propose_policy` incrementally
- bypass a ToolFence denial
- use native protected-action routes when ToolFence should mediate them

---

## Architecture

### Control plane

Responsible for:

- trusted task identity
- developer approval ceiling
- capability proposal validation
- policy compilation
- policy lifecycle

### Data plane

Responsible for:

- validating tool arguments
- deriving protected resource identity
- evaluating the active policy
- executing allowed calls
- blocking denied calls
- recording audit events

---

## Project Structure

```text
toolfence/
├── .bob/
│   ├── mcp.json
│   └── skills/
│       └── compile-task-policy/
│           └── SKILL.md
│
├── app/
│   ├── application.py
│   ├── bootstrap.py
│   ├── mcp_stdio.py
│   │
│   ├── gateway/
│   │   ├── audit.py
│   │   ├── dispatcher.py
│   │   └── mcp_server.py
│   │
│   └── policy/
│       ├── compiler.py
│       ├── controller.py
│       ├── evaluator.py
│       ├── matcher.py
│       ├── schema.py
│       └── store.py
│
├── benchmark/
│   ├── ground_truth.json
│   └── run_benchmark.py
│
├── config/
│   ├── capabilities.json
│   └── golden_task.json
│
├── mock_mcp/
│   ├── ci.py
│   ├── release.py
│   ├── repository.py
│   ├── secrets.py
│   └── tickets.py
│
├── tests/
│   ├── test_application.py
│   ├── test_benchmark.py
│   ├── test_controller.py
│   ├── test_gateway.py
│   ├── test_mcp_control_plane.py
│   └── test_policy.py
│
├── pyproject.toml
└── README.md
```

---

## Quick Start

### 1. Clone the repository

```powershell
git clone https://github.com/builtbyrehan/toolfence.git
cd toolfence
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### 4. Run tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

### 5. Run the benchmark

```powershell
.\.venv\Scripts\python.exe -m benchmark.run_benchmark
```

### 6. Run ToolFence as an MCP STDIO server

```powershell
.\.venv\Scripts\python.exe -m app.mcp_stdio
```

When launched by an MCP host such as IBM Bob, ToolFence communicates over STDIO and should not print unrelated output to stdout.

---

## IBM Bob MCP Configuration

Project-level MCP configuration lives in:

```text
.bob/mcp.json
```

Example:

```json
{
  "mcpServers": {
    "toolfence": {
      "command": "${workspaceFolder}/.venv/Scripts/python.exe",
      "args": [
        "-m",
        "app.mcp_stdio"
      ],
      "cwd": "${workspaceFolder}",
      "disabled": false
    }
  }
}
```

After connecting ToolFence, start a fresh Bob task so the current MCP tool schema is loaded.

---

## Security Properties

ToolFence currently demonstrates:

### Task-scoped authorization

Permissions are tied to a specific task.

### Least privilege

Bob proposes only the capabilities required for the current task.

### Trusted approval boundary

The developer approval ceiling is not supplied by the agent.

### Deterministic enforcement

The LLM does not decide whether a protected call is ultimately allowed.

### Resource-scoped permissions

A tool can be allowed for one resource and denied for another.

Example:

```text
repo.write project/src/*
→ allowed

repo.write project/tests/*
→ denied
```

### Separation of authorization and execution

ToolFence distinguishes:

```text
authorization: ALLOW
execution: SUCCEEDED
domain result: FAILED
```

For example, an authorized CI run may execute successfully while the tests themselves fail.

### Auditable decisions

Every validated protected request generates an audit event.

---

## Threat Model

ToolFence is designed to reduce risk from:

- over-privileged AI coding agents
- accidental use of unrelated tools
- attempts to access sensitive capabilities
- resource-scope confusion
- task drift
- permission over-requesting
- direct access to capabilities not required by the current task

ToolFence does not rely on prompt instructions alone for protected tool authorization.

The final ALLOW / DENY decision is deterministic.

---

## Current MVP Boundary

ToolFence currently protects actions routed through the **ToolFence MCP gateway**.

It does **not** provide host-level sandboxing of IBM Bob itself.

For example, this MVP does not technically prevent Bob from using:

- local shell access
- native filesystem access
- unrelated host integrations

if the host exposes those capabilities separately.

The included Bob skill instructs the agent not to bypass ToolFence, but that behavioral instruction is not equivalent to operating-system-level isolation.

This distinction is intentional and should be kept clear when evaluating the current MVP.

---

## Non-Goals

The current hackathon MVP does not attempt to provide:

- operating-system sandboxing
- full endpoint security
- production secrets management
- production deployment authorization
- enterprise identity federation
- a general-purpose policy language
- complete protection from every alternate host-side tool path

The goal is to demonstrate a focused security primitive:

> **Task-scoped deterministic authorization for AI coding-agent tool calls.**

---

## Design Decisions

### Why does Bob propose permissions?

The model understands the task semantically and can reason about what work is required.

### Why doesn't Bob approve its own proposal?

Because reasoning about what is useful is not the same as deciding what is trusted.

### Why keep the approval ceiling hidden?

If the agent sees the exact maximum policy first, it can simply mirror that ceiling rather than independently reasoning toward least privilege.

### Why is policy activation immutable?

Once a task policy is accepted, silently replacing it would create a privilege-expansion path.

### Why expose `task_context`?

Bob needs the canonical task text to submit a valid proposal, but it should not need access to trusted approval configuration.

---

## Future Work

Potential next steps include:

- visual security dashboard
- richer policy lifecycle controls
- human-approved policy changes
- signed task approvals
- persistent policy state
- persistent structured audit backend
- real GitHub / GitLab integration
- real CI provider integration
- policy visualization
- enterprise identity integration
- capability risk scoring
- organization-wide policy templates
- host-level sandbox integration
- multi-agent support
- real-world replay datasets

---

## Hackathon Demo Story

The shortest version of the ToolFence demo is:

```text
1. Developer gives Bob a normal coding task.

2. Bob reads the canonical task context.

3. Bob inspects available capabilities.

4. Bob proposes only the minimum required permissions.

5. ToolFence validates the proposal against a hidden trusted ceiling.

6. ToolFence activates an immutable task policy.

7. Bob attempts a forbidden secret read.

8. ToolFence returns DENY / NOT_EXECUTED.

9. Bob executes the legitimate bug-fix workflow.

10. ToolFence allows only approved actions.

11. CI passes.

12. Pull request is created.

13. Every protected action is auditable.
```

---

## Key Result

ToolFence demonstrates that an AI coding agent can remain useful without receiving unrestricted developer-tool authority.

```text
11 protected capabilities available
            ↓
6 capabilities granted for the task
            ↓
Forbidden actions blocked
            ↓
Legitimate task completed
            ↓
Every protected action audited
```

**Task-scoped security without removing agent autonomy.**

---

## Built With

- Python 3.11+
- Pydantic v2
- Model Context Protocol (MCP)
- IBM Bob
- Pytest
- JSONL audit logging

---

## Repository

**GitHub:** `builtbyrehan/toolfence`

---

## Status

**Hackathon MVP — core enforcement, MCP integration, Bob skill, golden demo, replay benchmark, and automated tests completed.**

Next focus:

- architecture visualization
- demo media
- dashboard
- final pitch
- hackathon submission packaging
