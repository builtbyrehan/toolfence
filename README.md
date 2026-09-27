# ToolFence

> **Task-Scoped Security for AI Coding Agents**  
> **Bob reasons. ToolFence enforces.**

ToolFence is a security gateway for AI coding agents that enforces **least-privilege, task-scoped access** to developer tools.

Instead of giving an AI agent broad access to repositories, CI, tickets, deployments, and secrets, ToolFence lets the agent propose the **minimum capabilities required for one task**. A trusted developer-defined approval ceiling is kept separate from the model, and every protected action is deterministically evaluated before execution.

Built for the **IBM Bob 2.0 Hackathon**.

---

## Why ToolFence?

AI coding agents are increasingly capable, but their tool access is often much broader than the task actually requires.

A typical coding agent may have access to:

- source repositories
- issue trackers
- CI pipelines
- pull requests
- deployment systems
- secrets
- production environments

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

IBM Bob can reason about what permissions are required. ToolFence independently decides whether those permissions and subsequent protected tool calls are allowed.

---

## Current System

ToolFence now includes the complete hackathon flow from Bob to a live security dashboard:

```text
IBM Bob
   ↓
ToolFence MCP
   ↓
Task Capability Contract
   ↓
Policy Engine
   ↓
Protected Tools
   ↓
Audit + Runtime Snapshot
   ↓
FastAPI Observability API
   ↓
React Security Dashboard
```

The authorization path and observability path are intentionally separate.

- **Authorization** uses the trusted in-memory policy store inside the ToolFence MCP process.
- **Observability** uses a sanitized runtime policy snapshot, append-only audit log, and benchmark report.
- The FastAPI dashboard bridge is **read-only** and never authorizes execution.

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

The agent can safely retrieve:

```json
{
  "task_id": "BUG-17-FIX",
  "task": "Fix BUG-17, run CI, and create a pull request."
}
```

The task context does **not** reveal the trusted approval ceiling.

### 2. Agent capability proposal

Bob determines the minimum access required and submits a complete capability proposal.

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

Bob cannot supply this ceiling. ToolFence validates the proposal against it before activating a policy.

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

### Active task policy

The active golden policy grants six capabilities:

| Tool | Resource |
|---|---|
| `ticket.get` | `BUG-17` |
| `repo.read` | `project/*` |
| `repo.write` | `project/src/*` |
| `ci.run` | `feature/BUG-17` |
| `ci.status` | `feature/BUG-17` |
| `pull_request.create` | `feature/BUG-17` |

Sensitive or unnecessary capabilities remain outside the task policy:

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

The secret backend was not executed.

This demonstrates that a capability can be visible to the agent while remaining unavailable to the active task policy.

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

Every protected ToolFence action records an audit event containing:

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

ToolFence deliberately avoids storing unnecessary backend payloads such as secret values or file contents.

Audit storage:

```text
runtime/audit.jsonl
```

---

## Runtime Policy Snapshot

ToolFence writes a sanitized runtime policy snapshot for observability:

```text
runtime/active_policy.json
```

The snapshot contains policy identity, lifecycle state, timestamps, and granted capability scopes.

It is **not an authorization source**.

The dispatcher and evaluator continue to use the trusted in-memory active policy store. Snapshot persistence is best-effort observability and cannot grant authority.

---

## Benchmark

ToolFence includes a deterministic authorization replay benchmark with **16 predefined scenarios** covering:

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

The latency values above are **authorization policy-evaluation time**, not end-to-end IBM Bob, MCP, HTTP, or backend execution latency.

### Privilege reduction

```text
11 available protected capabilities
6 granted capabilities

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

The repository includes:

```text
.bob/skills/compile-task-policy/SKILL.md
```

The skill teaches Bob to follow:

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
- use shell commands to discover trusted approval limits
- probe `propose_policy` incrementally
- bypass a ToolFence denial
- use alternate protected-action routes when ToolFence should mediate them

---

## FastAPI Observability API

ToolFence includes a read-only FastAPI bridge for the security dashboard.

Start it with:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.api.main:app --host 127.0.0.1 --port 8000 --reload
```

Available endpoints:

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | API health |
| `GET /api/task` | Canonical task context |
| `GET /api/policy` | Runtime policy snapshot |
| `GET /api/capabilities` | Full inventory with effective grants |
| `GET /api/audit` | Authorization evidence |
| `GET /api/benchmark` | Benchmark metrics |

Interactive API docs:

```text
http://127.0.0.1:8000/docs
```

The API is observability-only. It does not activate, expand, replace, or authorize policies.

---

## Security Dashboard

ToolFence now includes a live **React + TypeScript security console** backed by the FastAPI observability bridge.

The dashboard is a routed SPA with persistent shared navigation:

| Route | Page |
|---|---|
| `/dashboard` | Overview |
| `/dashboard/policy` | Policy |
| `/dashboard/activity` | Activity |
| `/dashboard/audit` | Audit |
| `/dashboard/benchmark` | Benchmark |

### Overview

Shows the canonical task, active policy state, granted capabilities, privilege reduction, audit-event count, and latest protected request.

### Policy

Shows the active Task Capability Contract, granted/excluded capability matrix, resource boundaries, and deterministic request flow.

### Activity

Shows protected-tool activity, ALLOW/DENY decisions, execution status, and reason codes.

### Audit

Shows authorization evidence for the task, including current and historical policy events.

### Benchmark

Shows the deterministic replay results, boundary accuracy, blocking rate, false-denial rate, privilege reduction, and policy-evaluation latency.

The frontend visualizes security state only. It never becomes part of the authorization decision path.

---

## Frontend Stack

- React
- TypeScript
- Vite
- Tailwind CSS v4
- React Router
- TanStack Query
- Motion
- Recharts
- Lucide React

React Router uses nested dashboard routes, so the sidebar and header remain persistent while only the main workspace changes.

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

### Observability plane

Responsible for:

- sanitized runtime policy snapshot
- audit-log reading
- benchmark-report reading
- read-only FastAPI endpoints
- dashboard visualization

The observability plane is intentionally separated from authorization.

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
│   ├── api/
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── health.py
│   │   │   ├── task.py
│   │   │   ├── policy.py
│   │   │   ├── capabilities.py
│   │   │   ├── audit.py
│   │   │   └── benchmark.py
│   │   ├── schemas/
│   │   └── services/
│   │
│   ├── gateway/
│   │   ├── audit.py
│   │   ├── dispatcher.py
│   │   └── mcp_server.py
│   │
│   ├── policy/
│   │   ├── compiler.py
│   │   ├── controller.py
│   │   ├── evaluator.py
│   │   ├── matcher.py
│   │   ├── runtime_snapshot.py
│   │   ├── schema.py
│   │   ├── snapshot_store.py
│   │   └── store.py
│   │
│   ├── application.py
│   ├── bootstrap.py
│   └── mcp_stdio.py
│
├── benchmark/
│   ├── ground_truth.json
│   └── run_benchmark.py
│
├── config/
│   ├── capabilities.json
│   └── golden_task.json
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── api/
│   │   ├── components/
│   │   ├── features/
│   │   ├── hooks/
│   │   ├── pages/
│   │   │   ├── landing/
│   │   │   └── dashboard/
│   │   ├── styles/
│   │   └── types/
│   ├── vite.config.ts
│   └── vercel.json
│
├── mock_mcp/
│   ├── ci.py
│   ├── release.py
│   ├── repository.py
│   ├── secrets.py
│   └── tickets.py
│
├── runtime/
│   ├── active_policy.json
│   ├── audit.jsonl
│   └── benchmark_report.json
│
├── tests/
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

### 2. Create and activate a Python virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install backend dependencies

```powershell
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### 4. Run the backend tests

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

### 7. Run the FastAPI dashboard bridge

In a separate terminal:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.api.main:app --host 127.0.0.1 --port 8000 --reload
```

### 8. Install and run the frontend

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173/
```

Dashboard:

```text
http://127.0.0.1:5173/dashboard
```

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

### Task-scoped authorization

Permissions are tied to a specific task.

### Least privilege

Bob proposes only the capabilities required for the current task.

### Trusted approval boundary

The developer approval ceiling is not supplied by the agent.

### Deterministic enforcement

The LLM does not decide whether a protected call is ultimately allowed.

### Resource-scoped permissions

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

### Read-only observability

The dashboard and FastAPI bridge visualize security state but do not become part of the authorization decision path.

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

ToolFence does not rely on prompt instructions alone for protected tool authorization. The final ALLOW/DENY decision is deterministic.

---

## Current MVP Boundary

ToolFence currently protects actions routed through the **ToolFence MCP gateway**.

It does **not** provide host-level sandboxing of IBM Bob itself.

For example, this MVP does not technically prevent Bob from using:

- local shell access
- native filesystem access
- unrelated host integrations

if the host exposes those capabilities separately.

The included Bob skill instructs the agent not to bypass ToolFence, but behavioral instruction is not equivalent to operating-system-level isolation.

This distinction is intentional and remains explicit in the MVP.

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

The goal is to demonstrate:

> **Task-scoped deterministic authorization for AI coding-agent tool calls.**

---

## Design Decisions

### Why does Bob propose permissions?

The model understands the task semantically and can reason about what work is required.

### Why doesn't Bob approve its own proposal?

Reasoning about what is useful is not the same as deciding what is trusted.

### Why keep the approval ceiling hidden?

If the agent sees the exact maximum policy first, it can simply mirror that ceiling instead of independently reasoning toward least privilege.

### Why is policy activation immutable?

Once a task policy is accepted, silently replacing it would create a privilege-expansion path.

### Why expose `task_context`?

Bob needs canonical task text to submit a valid proposal, but should not need access to trusted approval configuration.

### Why keep dashboard state separate from authorization?

The dashboard is for observability. Using its snapshot as an authorization source would weaken the trust boundary.

---

## Deployment Notes

The frontend uses `createBrowserRouter` with browser-history routes.

For Vercel/static hosting, `frontend/vercel.json` rewrites dashboard routes to `index.html`, allowing direct navigation and refreshes on:

```text
/dashboard
/dashboard/policy
/dashboard/activity
/dashboard/audit
/dashboard/benchmark
```

The frontend expects the FastAPI backend to be reachable through its configured API base URL.

---

## Future Work

Potential next steps include:

- richer policy lifecycle controls
- human-approved policy changes
- signed task approvals
- durable multi-task policy persistence
- persistent structured audit backend
- real GitHub/GitLab integration
- real CI provider integration
- richer policy visualization
- enterprise identity integration
- capability risk scoring
- organization-wide policy templates
- host-level sandbox integration
- multi-agent support
- real-world replay datasets
- production authentication for the dashboard/API
- real-time audit streaming with SSE or WebSockets

---

## Hackathon Demo Story

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
14. The dashboard visualizes active policy, activity, audit evidence, and benchmark results without becoming an authorization source.
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
            ↓
Runtime security state visualized
```

**Task-scoped security without removing agent autonomy.**

---

## Built With

### Security backend

- Python 3.11+
- Pydantic v2
- Model Context Protocol (MCP)
- IBM Bob
- FastAPI
- Uvicorn
- Pytest
- JSONL audit logging

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS v4
- React Router
- TanStack Query
- Motion
- Recharts
- Lucide React

---

## Repository

**GitHub:** `builtbyrehan/toolfence`

---

## Status

**Hackathon MVP — core policy enforcement, MCP integration, Bob skill, golden demo, runtime policy snapshot, FastAPI observability API, routed React dashboard, deterministic benchmark, and automated tests implemented.**

Current focus:

- final browser/demo verification
- demo media
- architecture visuals
- final pitch
- hackathon submission packaging
