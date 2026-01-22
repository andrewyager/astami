# Configuration

## Asterisk manager.conf

Ensure your Asterisk server has AMI enabled in `/etc/asterisk/manager.conf`:

```ini
[general]
enabled = yes
port = 5038
bindaddr = 0.0.0.0

[admin]
secret = your_secret_here
read = all
write = all
```

After changes, reload the manager module:

```bash
asterisk -rx "manager reload"
```

## Security Considerations

### Bind Address

For production, consider binding to a specific interface rather than `0.0.0.0`:

```ini
bindaddr = 127.0.0.1
```

Or use a private network interface:

```ini
bindaddr = 10.0.0.1
```

### User Permissions

Create users with minimal required permissions:

```ini
[monitoring]
secret = monitoring_secret
read = system,call
write =

[dialplan_reload]
secret = reload_secret
read = system
write = system,config
```

### Firewall

Restrict access to port 5038 at the firewall level:

```bash
# Allow only from specific hosts
iptables -A INPUT -p tcp --dport 5038 -s 10.0.0.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 5038 -j DROP
```

## Client Configuration

### Connection Timeout

Adjust the timeout for slow networks:

```python
# Default is 10 seconds
ami = AMIClient("localhost", 5038, "admin", "secret", timeout=30.0)
```

### Custom Port

If your AMI runs on a non-standard port:

```python
ami = AMIClient("localhost", 5039, "admin", "secret")
```
