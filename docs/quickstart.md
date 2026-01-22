# Quick Start

## Synchronous Usage

The synchronous client is ideal for scripts, Celery tasks, Django management commands, and other non-async contexts.

```python
from astami import AMIClient

with AMIClient("localhost", 5038, "admin", "secret") as ami:
    # Execute CLI commands
    response = ami.command("core show version")
    print(response.output)

    # Reload configuration
    ami.reload("pjsip")
```

## Asynchronous Usage

The async client is designed for asyncio applications like FastAPI, aiohttp, or any async Python code.

```python
import asyncio
from astami import AsyncAMIClient

async def main():
    async with AsyncAMIClient("localhost", 5038, "admin", "secret") as ami:
        # Execute CLI commands
        response = await ami.command("core show version")
        print(response.output)

        # Reload configuration
        await ami.reload("pjsip")

asyncio.run(main())
```

## Error Handling

```python
from astami import AMIClient, AMIError

try:
    with AMIClient("localhost", 5038, "admin", "wrong_password") as ami:
        ami.command("core show version")
except AMIError as e:
    print(f"AMI Error: {e}")
    if e.response:
        print(f"Response: {e.response.message}")
```
