"""
Offline model loader for the Velora agent. Uses llama-cpp-python to load a quantized GGUF model.
"""
from pathlib import Path
from llama_cpp import Llama

_llm = None

def get_model():
    """Load and cache the quantized GGUF model for the Velora agent."""
    global _llm
    if _llm is None:
        repo_root = Path(__file__).resolve().parents[3]
        model_path = repo_root / 'ai_models' / 'fine-tuned' / 'velora' / 'velora_q4.gguf'
        _llm = Llama(model_path=str(model_path))
    return _llm

def generate(prompt: str, max_tokens: int = 256, temperature: float = 0.7) -> str:
    """Generate a completion for the given prompt using the Velora GGUF model."""
    llm = get_model()
    result = llm(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        echo=False,
    )
    return result['choices'][0]['text']
