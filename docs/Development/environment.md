# Development Environment

## Purpose

This document describes the environment configuration required to run and develop the Smart Commerce Platform.

The project follows Django best practices by separating environment-specific settings from the application source code.

---

# Overview

Application configuration is managed through environment variables.

Sensitive information should never be hardcoded into the project or committed to version control.

This approach improves security while allowing different configurations for development, testing, and production environments.

---

# Environment Variables

The project relies on environment variables for configuration.

Typical variables include:

| Variable        | Purpose                      |
| --------------- | ---------------------------- |
| `SECRET_KEY`    | Django secret key            |
| `DEBUG`         | Enable or disable debug mode |
| `DATABASE_URL`  | Database connection string   |
| `ALLOWED_HOSTS` | Allowed host names           |

Additional variables may be introduced as the project evolves.

---

# Secret Key

The Django `SECRET_KEY` is treated as sensitive information.

It should:

* Exist only in environment variables
* Never be committed to Git
* Be different for each deployment environment

---

# Debug Configuration

The `DEBUG` setting controls development behavior.

Development:

```text id="lgnm67"
DEBUG=True
```

Production:

```text id="7j0m1n"
DEBUG=False
```

Production deployments should never enable debug mode.

---

# Database Configuration

Database configuration is centralized through `DATABASE_URL`.

The project uses `dj_database_url` to simplify database configuration across environments.

During development, SQLite is used by default.

The architecture supports replacing SQLite with production database engines such as PostgreSQL without changing application code.

---

# Static and Media Files

The application separates static assets from uploaded media.

Static files include:

* CSS
* JavaScript
* Fonts
* Icons

Media files include:

* Product images
* Future user uploads

This separation follows Django's recommended project structure.

---

# Installed Applications

Project functionality is organized into dedicated Django applications.

Current applications include:

* Core
* Accounts
* Stores
* Products

Additional applications can be introduced as new business domains are implemented.

---

# Third-Party Packages

The project currently integrates several third-party packages to simplify development.

Examples include:

* Django Crispy Forms
* Crispy Bootstrap 5
* Pillow
* dj-database-url

New dependencies should be evaluated before being introduced into the project.

---

# Local Development

Developers should configure their local environment before running the application.

Typical setup includes:

* Creating a virtual environment
* Installing project dependencies
* Configuring environment variables
* Running database migrations
* Creating an administrative user

These steps ensure a consistent development environment across different machines.

---

# Version Control

Environment-specific files should not be tracked by Git.

Typical examples include:

* `.env`
* Local database files
* Temporary files
* Python cache directories

The repository should contain only source code and documentation required to reproduce the project.

---

# Future Evolution

Future environments may include:

* Production configuration
* Staging environment
* Continuous Integration (CI)
* Containerized deployment
* Cloud hosting configuration

The environment management strategy should remain flexible as deployment requirements evolve.

---

# Related Documentation

* `Development/git-workflow.md`
* `Development/testing-strategy.md`
* `README.md`
* `Architecture/project-structure.md`
