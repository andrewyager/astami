# Use Cases

## Celery Tasks

```python
from celery import shared_task
from astami import AMIClient, AMIError

@shared_task
def reload_dialplan(server_host: str) -> bool:
    try:
        with AMIClient(server_host, 5038, "admin", "secret") as ami:
            response = ami.command("dialplan reload")
            return response.success
    except AMIError as e:
        logger.error(f"AMI error: {e}")
        return False
```

## Django Management Command

```python
from django.core.management.base import BaseCommand
from astami import AMIClient

class Command(BaseCommand):
    help = "Show Asterisk version"

    def handle(self, *args, **options):
        with AMIClient("localhost", 5038, "admin", "secret") as ami:
            response = ami.command("core show version")
            self.stdout.write(self.style.SUCCESS(response.output[0]))
```

## FastAPI Application

```python
from fastapi import FastAPI
from astami import AsyncAMIClient

app = FastAPI()

@app.get("/asterisk/version")
async def get_version():
    async with AsyncAMIClient("localhost", 5038, "admin", "secret") as ami:
        response = await ami.command("core show version")
        return {"version": response.output[0] if response.output else "Unknown"}
```

## Flask Application

```python
from flask import Flask, jsonify
from astami import AMIClient

app = Flask(__name__)

@app.route("/asterisk/version")
def get_version():
    with AMIClient("localhost", 5038, "admin", "secret") as ami:
        response = ami.command("core show version")
        return jsonify({"version": response.output[0] if response.output else "Unknown"})
```

## Monitoring Script

```python
#!/usr/bin/env python3
from astami import AMIClient, AMIError
import sys

def check_asterisk(host: str) -> int:
    try:
        with AMIClient(host, 5038, "admin", "secret") as ami:
            response = ami.ping()
            if response.success:
                print(f"OK - Asterisk at {host} is responding")
                return 0
            else:
                print(f"WARNING - Asterisk at {host} returned: {response.message}")
                return 1
    except AMIError as e:
        print(f"CRITICAL - Cannot connect to Asterisk at {host}: {e}")
        return 2

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    sys.exit(check_asterisk(host))
```

## Batch Operations

```python
from astami import AMIClient

servers = ["pbx1.example.com", "pbx2.example.com", "pbx3.example.com"]

for server in servers:
    with AMIClient(server, 5038, "admin", "secret") as ami:
        ami.reload("pjsip")
        print(f"Reloaded PJSIP on {server}")
```
