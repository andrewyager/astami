# Contributing

Contributions are welcome! Here's how to get started.

## Development Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/andrewyager/astami.git
    cd astami
    ```

2. Create a virtual environment:

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3. Install development dependencies:

    ```bash
    pip install -e ".[dev]"
    ```

## Running Tests

```bash
pytest tests/ -v
```

With coverage:

```bash
pytest tests/ -v --cov=astami --cov-report=html
```

## Code Quality

Before submitting a PR, ensure your code passes all checks:

```bash
# Linting
ruff check src/ tests/

# Formatting
black src/ tests/

# Type checking
mypy src/
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Code Style

- Follow PEP 8 guidelines
- Use type hints for all function parameters and return values
- Write docstrings for public functions and classes
- Keep functions focused and reasonably sized

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
