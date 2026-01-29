"""
Kiro Gateway - Example API Call

Before running:
1. pip install openai
2. kiro-gateway-cli start
3. Get your API key: kiro-gateway-cli status
"""

from openai import OpenAI


API_KEY = "Vpp59EPC97Ii5_PGGlkrYg" # View API Key from "kiro-gateway-cli status"

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key=API_KEY
)

response = client.chat.completions.create(
    model="claude-sonnet-4.5",
    messages=[{"role": "user", "content": "Hello!"}],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)

print()  # newline at end
