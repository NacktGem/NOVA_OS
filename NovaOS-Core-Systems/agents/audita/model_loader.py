"""
Offline model loader for the Audita agent. Uses llama-cpp-python to load a quantized GGUF model.
"""

from pathlib import Path
from llama_cpp import Llama
import threading

_lock = threading.Lock()
_llm = None

def get_model() -> Llama:
    """
    Load and cache the quantized GGUF model for the Audita agent.

    Returns:
        Llama: Loaded Llama model instance.
    """
    global _llm
    if _llm is None:
        with _lock:
            if _llm is None:  # Double-checked locking
                repo_root = Path(__file__).resolve().parents[3]
                model_path = repo_root / 'ai_models' / 'fine-tuned' / 'audita' / 'audita_q4.gguf'
                _llm = Llama(model_path=str(model_path), n_threads=4, n_ctx=2048)
    return _llm


def generate(prompt: str, max_tokens: int = 256, temperature: float = 0.7, top_k: int = 40, top_p: float = 0.9) -> str:
    """
    Generate a completion for the given prompt using the Audita GGUF model.

    Args:
        prompt (str): The prompt to generate a response for.
        max_tokens (int): Maximum number of tokens to generate.
        temperature (float): Sampling temperature.
        top_k (int): Top-K sampling.
        top_p (float): Top-P nucleus sampling.

    Returns:
        str: The generated response text.
    """
    llm = get_model()
    result = llm(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        echo=False
    )
    return result['choices'][0]['text'].strip()
