# API Reference

## Client Classes

### AsyncAMIClient

The async client for use in asyncio applications.

```python
AsyncAMIClient(
    host: str = "127.0.0.1",
    port: int = 5038,
    username: str = "",
    secret: str = "",
    timeout: float = 10.0,
)
```

### AMIClient

Synchronous wrapper for use in threaded applications, Celery tasks, etc.

```python
AMIClient(
    host: str = "127.0.0.1",
    port: int = 5038,
    username: str = "",
    secret: str = "",
    timeout: float = 10.0,
)
```

## Response Object

All methods return an `AMIResponse` object:

```python
@dataclass
class AMIResponse:
    raw: str              # Raw response string
    action_id: str        # ActionID from the request
    response: str         # Response status (Success, Error, etc.)
    message: str          # Message from Asterisk
    data: dict[str, str]  # All key-value pairs
    output: list[str]     # Output lines (for Command actions)

    @property
    def success(self) -> bool:
        """True if response indicates success"""
```

## Available Methods

### CLI Commands

Execute any Asterisk CLI command:

```python
response = ami.command("sip show peers")
for line in response.output:
    print(line)
```

### Asterisk Database (AstDB)

```python
# Store a value
ami.database_put("family", "key", "value")

# Retrieve a value
response = ami.database_get("family", "key")

# Delete a key
ami.database_del("family", "key")

# Delete entire family
ami.database_deltree("family")
```

### Call Origination

Originate to dialplan:

```python
ami.originate(
    channel="PJSIP/1000",
    context="default",
    exten="1001",
    priority=1,
    caller_id="Test Call <1234>",
    variables={"VAR1": "value1", "VAR2": "value2"},
)
```

Originate to application:

```python
ami.originate(
    channel="PJSIP/1000",
    application="Playback",
    data="hello-world",
)
```

### Channel Operations

```python
# Hangup a channel
ami.hangup("PJSIP/1000-00000001")

# Redirect a channel
ami.redirect(
    channel="PJSIP/1000-00000001",
    context="default",
    exten="1002",
    priority=1,
)

# Get channel variable
response = ami.get_var("PJSIP/1000-00000001", "CALLERID(num)")

# Set channel variable
ami.set_var("PJSIP/1000-00000001", "MY_VAR", "my_value")
```

### Configuration Reload

```python
# Reload specific module
ami.reload("pjsip")
ami.reload("dialplan")

# Reload all
ami.reload()
```

### Raw Actions

For actions not covered by convenience methods:

```python
response = ami.send_action({
    "Action": "QueueStatus",
    "Queue": "support",
})
```

### Connection Management

```python
# Ping to keep connection alive
ami.ping()

# Logoff from AMI
ami.logoff()
```

## Exceptions

### AMIError

Base exception for all AMI-related errors.

```python
from astami import AMIError

try:
    with AMIClient(...) as ami:
        ami.command("invalid command")
except AMIError as e:
    print(f"Error: {e}")
    if e.response:
        print(f"Response message: {e.response.message}")
```
