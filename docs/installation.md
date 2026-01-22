# Installation

## Requirements

- Python 3.10 or higher
- Network access to an Asterisk server with AMI enabled

## Install from PyPI

```bash
pip install astami
```

## Install from source

```bash
git clone https://github.com/andrewyager/astami.git
cd astami
pip install -e .
```

## Verify installation

```python
import astami
print(astami.__version__)
```
