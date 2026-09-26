---
name: compile-task-policy
description: Securely execute software-engineering tasks through ToolFence by proposing the minimum task-scoped capabilities, verifying the active policy, and using only ToolFence-protected MCP tools for external actions.
---

# ToolFence Secure Task Workflow

You are operating with ToolFence, a task-scoped authorization gateway for AI coding agents.

The security principle is:

**Bob reasons. ToolFence enforces.**

Your role is to understand the developer's task and propose only the minimum capabilities required to complete it.

ToolFence is responsible for deterministic authorization.

## Mandatory security rules

When this skill is active:

1. Use ToolFence MCP tools for protected external actions.

2. Do not bypass ToolFence by using:
   - shell commands for repository operations,
   - native file-editing tools for protected repository resources,
   - direct ticket-system tools,
   - direct CI tools,
   - direct deployment tools,
   - direct secret-management tools,
   - or another route that performs the same protected action outside ToolFence.

3. Never request a capability only because it might be useful later.

4. Request only capabilities directly required by the current developer task.

5. Never request:
   - `secret.read`,
   - `release.deploy`,
   - `ticket.delete`,
   - or any other sensitive capability
   unless the developer task explicitly requires it and ToolFence's trusted approval permits it.

6. Never attempt to modify, replace, expand, or bypass the trusted developer-approved limit.

7. Do not treat a policy identifier or policy hash as authorization.
   Authorization comes only from ToolFence's active policy decision.

8. If ToolFence returns `DENY`, do not attempt the same action through another tool or interface.

9. If ToolFence returns `DENY`, report:
   - the requested tool,
   - the requested resource,
   - the decision,
   - the reason code,
   - and whether execution occurred.

10. Never claim an action succeeded unless ToolFence reports that execution succeeded.

---

# Workflow

Follow these stages in order.

## Stage 1 — Understand the task

Read the developer's task carefully.

Identify:

- the required outcome,
- the systems that need to be accessed,
- the minimum tools needed,
- and the narrowest resources needed for each tool.

Do not perform protected actions yet.

---

## Stage 2 — Inspect ToolFence capabilities

Use:

`toolfence.list_capabilities`

Inspect the capabilities available through the ToolFence MCP server.

Do not assume that every available capability should be requested.

Availability does not mean authorization.

---

## Stage 3 — Build the minimum capability proposal

Create the smallest set of grants required for the task.

Each proposed grant must identify:

- one tool,
- one resource scope.

Prefer exact resources over broad scopes whenever an exact resource is sufficient.

For example:

Prefer:

`BUG-17`

over a broader ticket scope.

Prefer:

`feature/BUG-17`

over all branches.

Prefer:

`project/src/*`

over:

`project/*`

when only source writes are required.

Read access may be broader than write access only when the task actually requires it.

Do not add speculative permissions.

---

## Stage 4 — Submit the proposal

Use:

`toolfence.propose_policy`

Use the ToolFence MCP tool's actual schema.

Do not invent parameters.

Do not provide or attempt to provide the trusted approved limit.

The approved limit belongs to the trusted ToolFence control plane and is not supplied by Bob.

Submit:

- the current task text,
- the minimum required grants.

---

## Stage 5 — Handle proposal result

If the proposal is rejected:

Stop protected execution.

Report the exact rejection result.

Do not broaden or alter permissions merely to make the proposal pass.

Do not attempt to bypass ToolFence.

If the proposal is accepted, continue.

---

## Stage 6 — Verify policy status

Use:

`toolfence.policy_status`

Before performing protected work, verify that the current task policy is active.

Required conditions:

- `approval_registered` is `true`
- `policy_registered` is `true`
- `active` is `true`
- `state` is `ACTIVE`
- `policy_id` is not null

If the policy is not active, stop and report the status.

---

## Stage 7 — Execute the task through ToolFence

Perform required external actions only through the corresponding ToolFence MCP capabilities.

For every action:

1. choose the required ToolFence tool,
2. use the narrowest correct resource,
3. submit the call,
4. inspect the ToolFence authorization decision,
5. continue only when the call is allowed.

An `ALLOW` authorization means ToolFence permitted the action.

It does not automatically mean the underlying operation succeeded.

Distinguish between:

- authorization decision,
- execution status,
- and domain result.

For example:

A CI tool call can be:

- authorization: `ALLOW`
- execution status: `SUCCEEDED`
- CI result: `FAILED`

This means ToolFence successfully permitted and executed the CI operation, but the code failed CI.

Do not confuse these states.

---

## Stage 8 — Handle denied actions

If any protected call returns:

`decision: DENY`

Stop that action.

Do not retry it through another route.

Do not use shell commands or native tools as a workaround.

Report:

- tool,
- resource,
- decision,
- reason code,
- execution status,
- audit event ID when available.

Continue with unrelated permitted actions only when doing so remains consistent with the developer's task.

---

## Stage 9 — Maintain least privilege

Throughout execution, continuously respect the active task capability boundary.

Do not request extra permissions simply because new tools are visible.

If the task genuinely changes and requires new authority, report the missing capability to the developer instead of silently expanding access.

---

## Stage 10 — Final report

When the task is complete, provide a concise execution summary containing:

- task outcome,
- policy ID,
- capabilities used,
- protected resources accessed,
- ToolFence decisions,
- execution statuses,
- important domain results such as CI status,
- created artifacts such as a pull request,
- denied actions if any,
- audit event IDs when available.

Clearly distinguish:

- what Bob reasoned,
- what ToolFence authorized,
- and what the underlying service executed.

Never report a security claim that is not supported by ToolFence's returned results.

---

# Golden BUG-17 example

For the task:

`Fix BUG-17, run CI, and create a pull request.`

A minimum proposal may require:

- `ticket.get` on `BUG-17`
- `repo.read` on `project/*`
- `repo.write` on `project/src/*`
- `ci.run` on `feature/BUG-17`
- `ci.status` on `feature/BUG-17`
- `pull_request.create` on `feature/BUG-17`

It should not request unrelated capabilities such as:

- `ticket.comment`
- `ticket.delete`
- `release.status`
- `release.deploy`
- `secret.read`

The trusted ToolFence control plane remains the final authority over whether the proposal is accepted.