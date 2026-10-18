# Contributing to EasyDP Local PII Scanner

Thank you for your interest in contributing to **EasyDP Local PII Scanner**! We welcome bug fixes, documentation improvements, new file extractors, and validator enhancements.

---

## Code of Conduct

We are dedicated to providing a welcoming and supportive environment for all contributors. Please be respectful and constructive in all discussions.

---

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/easydp-in/pii-scanner.git
   cd pii-scanner
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

---

## Test-Driven Development (TDD) Workflow

We strictly adhere to TDD:
1. **Write a failing test first** in `tests/unit/`, `tests/integration/`, or `tests/e2e/`.
2. **Implement minimal code** to pass the test.
3. **Refactor and verify**:
   ```bash
   pytest
   ruff check .
   ruff format --check .
   mypy src/
   ```

---

## Mindful Git Commit Guidelines

We enforce the [Conventional Commits](https://www.conventionalcommits.org/) standard. All commit messages must follow the format:

```text
<type>(<scope>): <short description>

[optional body]

[optional footer(s)]
```

### Commit Types:
- `feat`: A new feature (e.g., adding an extractor for Word `.docx` or new checksum validator).
- `fix`: A bug fix (e.g., handling edge case in Verhoeff checksum).
- `test`: Adding or updating tests.
- `docs`: Documentation updates.
- `refactor`: Code changes that neither fix a bug nor add a feature.
- `chore`: Maintenance tasks, dependencies, build configurations.

### Examples:
- `feat(validator): add Mod-36 checksum validator for GSTIN numbers`
- `fix(csv): handle UTF-16 encoded customer export files`
- `test(aadhaar): add negative test cases for transposed digits`
- `docs(readme): add Homebrew and npm installation instructions`
