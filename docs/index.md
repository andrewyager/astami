# Astami

A modern, async-first Python client for the Asterisk Manager Interface (AMI).

[![PyPI version](https://badge.fury.io/py/astami.svg)](https://badge.fury.io/py/astami)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Modern Python**: Built for Python 3.10+ with full type hints
- **Async & Sync**: Both `AsyncAMIClient` and `AMIClient` (sync wrapper) available
- **Context Managers**: Automatic connection handling and cleanup
- **No Dependencies**: Pure Python, no external dependencies
- **Fully Typed**: Complete type annotations for IDE support
- **Convenience Methods**: High-level methods for common operations

## Why Astami?

- **Python 3.10+**: Uses modern Python features like `match` statements, union types with `|`, and proper async/await patterns
- **No Deprecated APIs**: Doesn't use deprecated asyncio patterns that break in Python 3.10+
- **Lightweight**: No dependencies beyond the Python standard library
- **Type Safe**: Full type hints for better IDE support and fewer bugs
- **Well Tested**: Comprehensive test suite

## Quick Example

```python
from astami import AMIClient

with AMIClient("localhost", 5038, "admin", "secret") as ami:
    response = ami.command("core show version")
    print(response.output)
```

## Credits

Developed by [Real World Technology Solutions](https://rwts.com.au).
