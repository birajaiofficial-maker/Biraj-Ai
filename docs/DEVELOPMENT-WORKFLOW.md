# BIRAJ AI — Development Workflow

## 1. Systems of record

- **Notion:** one canonical development task tracker, milestones, decisions, progress and change records.
- **GitHub:** source code, branches, commits, pull requests, CI and technical specifications.
- **ChatGPT:** development assistant used to inspect, plan, implement, test, review and document. It is not the deployed AI runtime.

Do not create a second task tracker in another Notion database. Do not store credentials or secrets in Notion/GitHub.

## 2. Before starting a task

1. Open the Development Dashboard and current project.
2. Search the canonical Task Tracker by module, feature, error text and task wording.
3. Reuse/update an existing task if it covers the same outcome; do not create a duplicate.
4. Confirm acceptance criteria, dependencies, priority and owner.
5. Inspect the repository, current branch, open PRs, working tree and relevant tests.
6. Confirm the task's branch and whether an open PR already contains the work.
7. Record the Task ID in the branch/PR description.

## 3. Implementation cycle

1. Read architecture, decision log and module spec.
2. Make one focused change for one task.
3. Add or update tests for success, invalid input, failure and security boundaries.
4. Run relevant tests and record the exact command and result.
5. Review diff for secrets, unintended provider calls, unrelated changes and duplicated logic.
6. Update technical documentation and Notion task/change record.
7. Open or update a PR; do not merge without explicit approval.

## 4. Status flow

Backlog → Ready → In Progress → Review → Testing → Done

Blocked is a separate state and requires a recorded blocker. Done means acceptance criteria are met and test evidence exists, not merely that code was written.

## 5. Branch policy

- `main`: stable integrated code.
- `work/open-weight-core`: current migration baseline and sequential development branch.
- One coherent task/milestone per PR.
- No duplicate branches for work already under review.
- Do not edit `main` directly.
- Preserve old experimental branches until their unique commits have been reviewed and either ported or explicitly retired.
- No automatic merge, branch deletion or force-push.

## 6. Required PR description

Include Task ID, purpose, scope, files/modules changed, tests run with actual results, security/privacy impact, screenshots or API examples if relevant, and known limitations.

## 7. Session closeout

Before ending a coding session:
- update the existing Task record and status;
- attach commit/PR link;
- record tests actually run;
- add material decisions to the Decision Register;
- add meaningful changes to the Change Log;
- record blockers and exact next step;
- ensure no duplicate tasks were created.

## 8. Safety boundaries

No paid service, cloud/GPU provisioning, production deployment, external model API, secret rotation, data deletion, PR merge or branch deletion without explicit approval.
