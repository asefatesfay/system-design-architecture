# AWS Bedrock Tutorial

This tutorial demonstrates how to use AWS Bedrock with the Converse API, including basic usage, multi-turn conversations, and tool use.

## Prerequisites

- AWS account with Bedrock access
- AWS credentials configured
- Python 3.8+
- Dependencies installed (run `uv sync` or `pip install -r requirements.txt`)

## AWS Profile Configuration

All scripts support flexible AWS profile configuration through three methods (in order of precedence):

1. **Command-line argument**: `--profile-name`
2. **Environment variable**: `AWS_PROFILE`
3. **Default**: Falls back to `'default'` profile

### Usage Examples

```bash
# Using command-line argument
uv run bedrock-converse-api.py --profile-name assefa-federated

# Using environment variable
export AWS_PROFILE=assefa-federated
uv run bedrock-converse-api.py

# Using default profile
uv run bedrock-converse-api.py
```

## Scripts

### 1. bedrock-converse-api.py
Basic example of using the Bedrock Converse API with a simple prompt.

```bash
uv run bedrock-converse-api.py --profile-name your-profile
```

### 2. multi-turn-conversation.py
Demonstrates maintaining conversation context across multiple turns.

```bash
uv run multi-turn-conversation.py --profile-name your-profile
```

### 3. tool-use.py
Shows how to use tools with Bedrock, including function calling and weather API simulation.

```bash
uv run tool-use.py --profile-name your-profile
```

## Help

All scripts support the `--help` flag for usage information:

```bash
uv run tool-use.py --help
```
