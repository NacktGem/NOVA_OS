

"""
Lyra Formatter — Caption Stylist & Semantic Enhancer
Applies intelligent formatting to user-submitted captions, content, and promotional text.
"""

import re
from datetime import datetime
from config.audit_logger import log_event

EMOJI_MAP = {
    "fire": "🔥",
    "rose": "🌹",
    "heart": "❤️",
    "star": "⭐",
    "wink": "😉",
    "sparkle": "✨",
    "lock": "🔒",
    "kiss": "💋"
}

NSFW_KEYWORDS = [
    "nude", "raw", "explicit", "pussy", "cock", "dick", "wet", "hard", "suck", "ride", "spank", "moan"
]

class LyraFormatter:
    def __init__(self):
        self.timestamp = datetime.now().isoformat()

    def enhance_caption(self, text: str) -> str:
        original = text
        text = self._normalize_whitespace(text)
        text = self._auto_emphasize_keywords(text)
        text = self._insert_emojis(text)
        text = self._enforce_signature(text)
        log_event("caption_enhanced", {
            "original": original,
            "enhanced": text,
            "timestamp": self.timestamp
        })
        return text

    def _normalize_whitespace(self, text: str) -> str:
        return re.sub(r'\s+', ' ', text).strip()

    def _auto_emphasize_keywords(self, text: str) -> str:
        for keyword in NSFW_KEYWORDS:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            replacement = f"*{keyword.upper()}*"
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    def _insert_emojis(self, text: str) -> str:
        for word, emoji in EMOJI_MAP.items():
            pattern = r'\b' + re.escape(word) + r'\b'
            text = re.sub(pattern, f"{word} {emoji}", text, flags=re.IGNORECASE)
        return text

    def _enforce_signature(self, text: str) -> str:
        if "🌹" not in text:
            return text + " 🌹 #BlackRoseCollective"
        return text

# Example usage:
# formatter = LyraFormatter()
# enhanced = formatter.enhance_caption("Feeling raw and wet tonight. Come ride.")
# print(enhanced)