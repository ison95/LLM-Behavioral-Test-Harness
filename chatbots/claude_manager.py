import os
import anthropic
from dotenv import load_dotenv


# Fetch Claude API Key
def setup():
    load_dotenv()
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        raise RuntimeError("ERROR: CLAUDE_API_KEY not set in the .env file.")
        return

    client = anthropic.Anthropic(api_key=api_key)
    return client


# Handle prompting and response gathering
def prompt_claude(client: anthropic.Anthropic, model: str, prompt: str) -> str:
    model_resp = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return model_resp.content[0].text

