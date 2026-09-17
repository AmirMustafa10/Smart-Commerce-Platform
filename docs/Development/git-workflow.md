# Git Workflow

## Purpose

This document describes the Git workflow used during the development of the Smart Commerce Platform.

The goal is to maintain a clean commit history, isolate new features, and ensure that changes are reviewed before being merged into the main branch.

---

# Branching Strategy

Development follows a feature branch workflow.

Each new feature, enhancement, or bug fix is implemented in its own branch before being merged into the main branch.

Typical workflow:

```text
main
 │
 ├───────────────┐
 │               │
 ▼               ▼
feature/auth   feature/products
```

This approach keeps the `main` branch stable while allowing multiple features to be developed independently.

---

# Feature Development

Each feature branch should contain work related to a single business objective.

Examples include:

* Authentication improvements
* Product management
* Store management
* Documentation updates
* Testing improvements

Mixing unrelated features in the same branch should be avoided.

---

# Commit Strategy

Commits should represent logical units of work.

Each commit should describe **what changed**, not **how long it took** or **what files were modified**.

Examples:

* Add merchant registration workflow
* Implement product image validation
* Refactor tenant ownership model
* Add product management tests

Commit messages should remain concise and meaningful.

---

# Pull Requests

Completed feature branches should be merged into `main` through a Pull Request.

A Pull Request should:

* Focus on one feature
* Contain a clear description
* Pass all tests
* Be reviewed before merging whenever collaboration is involved

---

# Keeping Main Stable

The `main` branch should always represent a stable version of the project.

Incomplete features should remain in their feature branches until they are ready.

Direct development on `main` should be avoided whenever possible.

---

# Synchronizing Local Repository

After a feature branch has been merged:

1. Switch to `main`.
2. Pull the latest changes.
3. Delete the local feature branch if it is no longer needed.
4. Create a new feature branch for the next task.

This keeps the local repository clean and synchronized with the remote repository.

---

# Documentation Workflow

Documentation evolves alongside the codebase.

Architectural decisions, design changes, and important implementation choices should be documented as development progresses rather than postponed until the end of the project.

---

# Best Practices

Development follows these practices:

* Keep commits focused.
* Keep branches short-lived.
* Write meaningful commit messages.
* Keep `main` deployable.
* Update documentation alongside implementation.
* Maintain automated tests for new features.

---

# Future Evolution

As the project grows, the workflow may include:

* Branch protection rules
* Automated CI pipelines
* Code review requirements
* Release branches
* Version tagging
* Automated deployments

---

# Related Documentation

* `Development/testing-strategy.md`
* `Decisions/design-principles.md`
* `Architecture/project-structure.md`
* `README.md`
