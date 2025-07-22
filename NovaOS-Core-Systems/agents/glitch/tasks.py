"""
Task runner for the Glitch agent. Invokes the offline GGUF model loader and generates responses.
"""
from .model_loader import generate

def run_task(prompt: str, max_tokens: int = 256, temperature: float = 0.7) -> str:
    """Run the Glitch agent with the given prompt and return the generated text."""
    return generate(prompt, max_tokens=max_tokens, temperature=temperature)
