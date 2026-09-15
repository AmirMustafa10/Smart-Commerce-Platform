# ADR-010: Organize Automated Tests by Application Layer

## Status

Accepted

---

## Context

The platform contains multiple Django applications with different responsibilities.

As the application grows, maintaining all tests in a single location becomes difficult and reduces readability.

The project requires a testing structure that allows developers to:

- Easily locate tests.
- Maintain tests alongside application responsibilities.
- Scale testing as new features are introduced.

A decision was required on how automated tests should be organized.

---

## Decision

Organize automated tests by Django application and separate them by application layer.

Each application maintains its own test structure.

Example:

```text
app/
│
├── tests/
│   ├── test_models.py
│   ├── test_forms.py
│   └── test_views.py
```

Tests are separated based on responsibility:

### Model Tests

Responsible for testing:

- Database behavior.
- Model validation.
- Relationships.
- Business rules inside models.

### Form Tests

Responsible for testing:

- User input validation.
- Form behavior.
- Business validation rules.

### View Tests

Responsible for testing:

- Authentication requirements.
- Permissions.
- Request/response behavior.
- User workflows.

---

## Alternatives Considered

### Single Test File for the Entire Project

#### Advantages

- Simple initial setup.
- Easy to create at the beginning.

#### Disadvantages

- Becomes difficult to navigate as the project grows.
- Mixes unrelated application logic.
- Reduces maintainability.

**Decision:** Rejected.

---

### Tests Grouped Only by Feature

Example:

```text
tests/
├── authentication/
├── products/
└── stores/
```

#### Advantages

- Groups complete user features together.

#### Disadvantages

- May mix models, forms, and views.
- Less aligned with Django application structure.
- Can become difficult when features overlap.

**Decision:** Rejected.

---

### Application-Based Layered Testing

#### Advantages

- Matches Django project organization.
- Easier maintenance.
- Clear responsibility separation.
- Scales with new applications.

#### Disadvantages

- Requires more test files initially.
- Developers need to follow the structure consistently.

**Decision:** Accepted.

---

## Consequences

### Positive

- Easier navigation and maintenance.
- Better separation of responsibilities.
- Faster debugging when tests fail.
- Supports growth of multiple Django applications.
- Encourages testing each application independently.

### Negative

- More files compared to a simple test structure.
- Requires consistent organization.

---

## Future Considerations

The testing strategy can evolve with project growth by adding:

- Continuous Integration pipelines.
- Code coverage tracking.
- Integration tests.
- End-to-end testing.
- Automated test execution before deployment.

---

## Related Documentation

- `Development/testing-strategy.md`
- `Architecture/project-structure.md`
- `Development/git-workflow.md`
