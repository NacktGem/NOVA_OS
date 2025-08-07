"""
Task runner for the Lyra agent. Invokes LLM, caption formatter, and generation tools.
"""

from .model_loader import generate
from .caption_generator import generate_caption, suggest_tags, refine_style

def run_task(task_type: str, payload: dict) -> str:
    """
    Dispatch task to appropriate toolset based on task_type.
    
    Supported task_types:
    - 'llm_prompt': Generate raw text from prompt
    - 'caption': Generate a smart caption from content/context
    - 'tags': Suggest styled hashtags or metadata tags
    - 'style_refine': Improve or rephrase a caption for tone/clarity
    """
    if task_type == "llm_prompt":
        return generate(
            payload.get("prompt", ""),
            max_tokens=payload.get("max_tokens", 256),
            temperature=payload.get("temperature", 0.7)
        )
    elif task_type == "caption":
        return generate_caption(
            content=payload.get("content", ""),
            tone=payload.get("tone", "moody"),
            platform=payload.get("platform", "BlackRose")
        )
    elif task_type == "tags":
        return suggest_tags(
            content=payload.get("content", ""),
            theme=payload.get("theme", "luxury")
        )
    elif task_type == "style_refine":
        return refine_style(
            text=payload.get("text", ""),
            goal=payload.get("goal", "elevate branding")
        )
    else:
        raise ValueError(f"Unknown task_type: {task_type}")