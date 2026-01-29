<div align="center">

# 👻 Kiro Gateway

**Proxy gateway for Kiro API - Use Claude models with OpenAI-compatible tools**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

*Use Claude models from Kiro IDE with Cursor, Cline, Claude Code, OpenAI SDK, LangChain, and other OpenAI-compatible tools*

Based on [Jwadow/kiro-gateway](https://github.com/Jwadow/kiro-gateway)

</div>

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [Kiro IDE](https://kiro.dev/) installed and logged in

> ⚠️ **Note:** This fork only supports **Kiro IDE** mode. For other authentication methods (kiro-cli, AWS SSO, etc.), please refer to the [original repository](https://github.com/Jwadow/kiro-gateway).

### Installation

```bash
pip install git+https://github.com/clipdalle/kiro-gateway.git
```

### Setup

```bash
kiro-gateway-cli init
```

This will:
1. Auto-detect your Kiro IDE credentials
2. Generate an API key for your proxy
3. Ask if you want to start the server

```
  👻 Kiro Proxy Setup

  ? Select credentials source:

    ❯ 1. Kiro IDE (auto-detect)
      2. kiro-cli (not available)
      3. Manual file path (e.g. ~/.aws/sso/cache/kiro-auth-token.json)

  🔍 Searching for Kiro IDE credentials...
  ✅ Found: ~/.aws/sso/cache/kiro-auth-token.json

  ? Server port [8000]: 

  🔑 Generated API Key: OV_ij_LImltP3gztbaexRA

  ✅ Setup complete!
```

### Start Server

```bash
kiro-gateway-cli start
```

Output:
```
  👻 Kiro Proxy

  ✅ Kiro Proxy is running!

  Connection Info:

    Base URL:  http://localhost:8000/v1
    API Key:   OV_ij_LImltP3gztbaexRA
    Models:    claude-sonnet-4.5, claude-sonnet-4, claude-haiku-4.5
```

---

## 🤖 Available Models

| Model | Description |
|-------|-------------|
| `claude-sonnet-4.5` | Latest Sonnet, balanced performance |
| `claude-haiku-4.5` | Fast responses, simple tasks |
| `claude-sonnet-4` | Previous generation |

> Model availability depends on your Kiro tier (free/paid).

---

## 💡 Usage Examples

### Python (OpenAI SDK)

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="YOUR_API_KEY"  # Run `kiro-gateway-cli status` to view
)

response = client.chat.completions.create(
    model="claude-sonnet-4.5",
    messages=[{"role": "user", "content": "Hello!"}],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### Cursor / Cline / Continue

```
API Base URL: http://localhost:8000/v1
API Key:      YOUR_API_KEY  # Run `kiro-gateway-cli status` to view
Model:        claude-sonnet-4.5
```

### cURL

```bash
# Replace YOUR_API_KEY with the key from `kiro-gateway-cli status`
curl http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "claude-sonnet-4.5", "messages": [{"role": "user", "content": "Hello!"}]}'
```

---

## 📋 CLI Commands

| Command | Description |
|---------|-------------|
| `kiro-gateway-cli init` | Interactive setup wizard |
| `kiro-gateway-cli start` | Start the proxy server |
| `kiro-gateway-cli start --port 9000` | Start on custom port |
| `kiro-gateway-cli status` | Show current configuration |

---

## ✨ Features

- ✅ **OpenAI-compatible API** - Works with any OpenAI-compatible tool
- ✅ **Anthropic-compatible API** - Native `/v1/messages` endpoint
- ✅ **Streaming** - Full SSE streaming support
- ✅ **Extended Thinking** - Reasoning support
- ✅ **Vision Support** - Send images to model
- ✅ **Tool Calling** - Function calling support
- ✅ **Auto Token Refresh** - Automatic credential management

---

## 🔗 References

- **Original Project:** [Jwadow/kiro-gateway](https://github.com/Jwadow/kiro-gateway) - Full documentation and all authentication modes
- **Kiro IDE:** [kiro.dev](https://kiro.dev/)

---

## 📜 License

AGPL-3.0 - See [LICENSE](LICENSE) for details
