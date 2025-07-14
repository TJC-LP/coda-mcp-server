# Contributing to Coda MCP Server

We love your input! We want to make contributing to Coda MCP Server as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## We Develop with Github

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## We Use [Github Flow](https://guides.github.com/introduction/flow/index.html)

Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](LICENSE) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using Github's [issues](https://github.com/yourusername/coda-mcp-server/issues)

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/yourusername/coda-mcp-server/issues/new); it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Development Setup

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/coda-mcp-server.git
   cd coda-mcp-server
   ```

3. **Create and activate a virtual environment**:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   uv sync --all-extras
   ```

5. **Install pre-commit hooks**:
   ```bash
   uv run pre-commit install
   ```

6. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your Coda API token
   ```

## Testing

Run the test suite:
```bash
uv run pytest
```

Run tests with coverage:
```bash
uv run pytest --cov=src/coda_mcp_server --cov-report=html
```

## Code Style

We use several tools to maintain code quality:

- **ruff**: For linting and formatting
- **mypy**: For type checking
- **black**: For code formatting (via ruff)

These are automatically run via pre-commit hooks, but you can also run them manually:

```bash
# Run all pre-commit hooks
uv run pre-commit run --all-files

# Or run individually
uv run ruff check src/
uv run ruff format src/
uv run mypy src/
```

## Pull Request Process

1. Update the README.md with details of changes to the interface, if applicable.
2. Update the tests to cover your changes.
3. The PR will be merged once you have the sign-off of at least one maintainer.

## Code of Conduct

Please note we have a [Code of Conduct](CODE_OF_CONDUCT.md), please follow it in all your interactions with the project.

## License

By contributing, you agree that your contributions will be licensed under its MIT License.