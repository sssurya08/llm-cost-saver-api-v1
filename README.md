# LLM Cost Saver API

A simple API that automatically routes your LLM requests to the cheapest model that can handle the job — saving you money without changing how you build.

---

## What It Does

Instead of always sending every request to an expensive model, this API looks at your prompt and your preferred mode, then decides whether to use a cheap model or an expensive one. You get back the response, which model was used, how much it cost, and how much you saved compared to always using the expensive model.

---

## Setup

**Base URL**
```
http://localhost:8000
```

**Authentication**

Every request to `/chat` requires an API key passed as a Bearer token in the `Authorization` header:
```
Authorization: Bearer testkey123
```

---

## Endpoints

### `POST /chat`

Send a prompt and get a response back from the best model for the job.

**Request JSON**
```json
{
  "prompt": "Summarize the French Revolution in one sentence.",
  "mode": "cheap"
}
```

**Response JSON**
```json
{
  "response": "The French Revolution was a period of radical political and societal change in France from 1789 to 1799.",
  "model_used": "cheap-model",
  "tokens": 9,
  "estimated_cost": 0.000009,
  "estimated_savings": 0.000081
}
```

---

## Calling /chat

### curl
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer testkey123" \
  -d '{"prompt": "Summarize the French Revolution in one sentence.", "mode": "cheap"}'
```

### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    headers={
        "Authorization": "Bearer testkey123",
        "Content-Type": "application/json",
    },
    json={
        "prompt": "Summarize the French Revolution in one sentence.",
        "mode": "cheap",
    }
)

print(response.json())
```

---

## Modes

| Mode | Behavior |
|------|----------|
| `cheap` | Routes to the cheapest model if the prompt is under 200 tokens. Best for simple or short tasks. |
| `fast` | Routes to the expensive model regardless of prompt length. Use for complex tasks that need higher quality. |

---

## Understanding Costs

**`estimated_cost`** — the actual cost of the request based on which model was used and how many tokens were in your prompt.

**`estimated_savings`** — how much you saved compared to if you had sent the same request to the expensive model every time. This is always `0.00` when the expensive model is used, and a positive number whenever the cheap model is used instead.

These fields are returned on every response so you can track your savings over time. All logged requests are also stored and viewable at `GET /logs`.

---

## Other Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check — confirms the API is running |
| `/chat/demo` | GET | Returns a sample response without needing to POST |
| `/logs` | GET | Returns all logged requests from the database |
| `/docs` | GET | Interactive Swagger UI for testing the API |
