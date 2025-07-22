

"""
Echo Agent — Identity Handler
Manages personality registration and maps emotional tone to unique user IDs.
"""

import json
from pathlib import Path
from typing import Dict
from datetime import datetime
from textblob import TextBlob
from config.audit_logger import log_event

IDENTITY_DB = Path(__file__).resolve().parents[3] / "data" / "echo" / "user_tone_profiles.json"
IDENTITY_DB.parent.mkdir(parents=True, exist_ok=True)

def register_user(user_id: str, sample_message: str) -> Dict:
    """
    Registers a new user identity with initial tone fingerprinting.

    Args:
        user_id (str): Unique user ID.
        sample_message (str): Sample message or description from user.

    Returns:
        dict: Registered profile entry.
    """
    profile = {
        "user_id": user_id,
        "registered_at": datetime.utcnow().isoformat(),
        "baseline": _analyze_text(sample_message),
        "updated_at": datetime.utcnow().isoformat()
    }

    existing = _load_profiles()
    existing[user_id] = profile
    _save_profiles(existing)

    log_event("identity_registered", profile)
    return profile


def update_profile(user_id: str, new_message: str) -> Dict:
    """
    Updates a user's tone profile with a new sample message.

    Args:
        user_id (str): Unique user ID.
        new_message (str): New message text.

    Returns:
        dict: Updated profile entry.
    """
    existing = _load_profiles()
    if user_id not in existing:
        raise ValueError(f"User {user_id} not found in identity DB.")

    analysis = _analyze_text(new_message)
    existing[user_id]["baseline"] = analysis
    existing[user_id]["updated_at"] = datetime.utcnow().isoformat()

    _save_profiles(existing)
    log_event("identity_updated", existing[user_id])
    return existing[user_id]


def get_user_profile(user_id: str) -> Dict:
    """
    Retrieves the user's tone profile.

    Args:
        user_id (str): Unique user ID.

    Returns:
        dict: Profile data.
    """
    existing = _load_profiles()
    return existing.get(user_id, {})


def _analyze_text(text: str) -> Dict:
    """
    Analyzes emotional tone of text using sentiment polarity and subjectivity.

    Args:
        text (str): Input text.

    Returns:
        dict: {
            "polarity": float,
            "subjectivity": float,
            "classification": str
        }
    """
    blob = TextBlob(text)
    polarity = round(blob.sentiment.polarity, 4)
    subjectivity = round(blob.sentiment.subjectivity, 4)

    if polarity > 0.3:
        classification = "positive"
    elif polarity < -0.3:
        classification = "negative"
    elif abs(polarity) < 0.1:
        classification = "neutral"
    else:
        classification = "mixed"

    return {
        "polarity": polarity,
        "subjectivity": subjectivity,
        "classification": classification
    }


def _load_profiles() -> Dict:
    if IDENTITY_DB.exists():
        with open(IDENTITY_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_profiles(data: Dict):
    with open(IDENTITY_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)