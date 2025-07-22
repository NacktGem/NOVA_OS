

"""
Lyra Scripts — Content Styling & Creator Assistant
Provides post-ready caption stylization, theme-aware rewrites, and media description enhancements.
"""

from datetime import datetime
from lyra_formatter import LyraFormatter
from config.audit_logger import log_event

class LyraScriptEngine:
    def __init__(self):
        self.formatter = LyraFormatter()

    def generate_caption_variants(self, base_text: str) -> dict:
        """
        Returns styled variants of a caption in different tones for social, sensual, or promotional use.
        """
        log_event("caption_variant_requested", {"base": base_text})
        return {
            "tease": self.formatter.enhance_caption(f"Can you handle this? {base_text}"),
            "romantic": self.formatter.enhance_caption(f"Soft moments and whispered secrets... {base_text}"),
            "explicit": self.formatter.enhance_caption(f"{base_text} — raw, real, and all yours."),
            "promo": self.formatter.enhance_caption(f"{base_text} 🔥 Unlock the full set now."),
        }

    def rewrite_description_for_theme(self, text: str, theme: str) -> str:
        """
        Rewrites a description based on target theme: 'soft', 'dominant', 'mystical', 'luxury'
        """
        themed_prompt = {
            "soft": f"Gentle light, silky textures, and warm gazes. {text}",
            "dominant": f"Power drips from every move. You obey, or you watch. {text}",
            "mystical": f"Veiled in candlelight and shadow. The unknown pulls you in. {text}",
            "luxury": f"Champagne skin, high gloss, and designer sin. {text}"
        }.get(theme.lower(), text)

        result = self.formatter.enhance_caption(themed_prompt)
        log_event("description_rewritten", {"theme": theme, "output": result})
        return result

    def assist_creator_post(self, text: str, intent: str) -> str:
        """
        Assists creator with a post suggestion based on posting intent.
        Supported intents: 'morning tease', 'night drop', 'premium pitch', 'daily vibe'
        """
        intent_templates = {
            "morning tease": f"Good morning, lovers... {text}",
            "night drop": f"It’s late. And I’m still thinking about this: {text}",
            "premium pitch": f"This one’s locked away. 🔒 Want in? {text}",
            "daily vibe": f"Today’s energy? {text} Let’s live it."
        }

        caption = intent_templates.get(intent.lower(), text)
        final = self.formatter.enhance_caption(caption)
        log_event("post_assisted", {"intent": intent, "final_caption": final})
        return final

# Example usage:
# engine = LyraScriptEngine()
# variants = engine.generate_caption_variants("Feeling raw and wet tonight.")
# print(variants["explicit"])