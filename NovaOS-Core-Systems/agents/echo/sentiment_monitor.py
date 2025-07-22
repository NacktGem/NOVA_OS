

"""
Echo Agent — Real-Time Sentiment Monitor
Analyzes messages, logs sentiment trends, and flags emotional spikes.
"""

import datetime
import pandas as pd
from textblob import TextBlob
from config.audit_logger import log_event
from pathlib import Path
from typing import List, Dict

# Sentiment thresholds
THRESHOLDS = {
    "positive": 0.3,
    "negative": -0.3,
    "neutral_margin": 0.15,
    "spike_threshold": 0.6
}

# Log directory
LOG_DIR = Path(__file__).resolve().parents[3] / "logs" / "echo"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "sentiment_log.parquet"


def analyze_message(text: str) -> Dict:
    """
    Analyzes a single message and returns sentiment data.

    Args:
        text (str): Message text.

    Returns:
        dict: {
            "timestamp": str,
            "polarity": float,
            "subjectivity": float,
            "classification": str
        }
    """
    blob = TextBlob(text)
    polarity = round(blob.sentiment.polarity, 4)
    subjectivity = round(blob.sentiment.subjectivity, 4)

    if polarity >= THRESHOLDS["positive"]:
        classification = "positive"
    elif polarity <= THRESHOLDS["negative"]:
        classification = "negative"
    elif abs(polarity) < THRESHOLDS["neutral_margin"]:
        classification = "neutral"
    else:
        classification = "mixed"

    return {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "polarity": polarity,
        "subjectivity": subjectivity,
        "classification": classification
    }


def log_sentiment(data: Dict):
    """
    Logs a sentiment entry to disk.

    Args:
        data (dict): Sentiment record.
    """
    if LOG_FILE.exists():
        df = pd.read_parquet(LOG_FILE)
    else:
        df = pd.DataFrame()

    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_parquet(LOG_FILE, index=False)

    log_event("sentiment_monitor_entry", data)


def flag_spikes(window: int = 5) -> List[Dict]:
    """
    Detects emotional spikes over recent sentiment logs.

    Args:
        window (int): Number of recent entries to evaluate.

    Returns:
        List[Dict]: List of flagged spikes.
    """
    if not LOG_FILE.exists():
        return []

    df = pd.read_parquet(LOG_FILE)
    recent = df.tail(window)

    spikes = []
    for _, row in recent.iterrows():
        if abs(row["polarity"]) >= THRESHOLDS["spike_threshold"]:
            spike = row.to_dict()
            spike["flagged"] = True
            spikes.append(spike)
            log_event("sentiment_spike_flagged", spike)

    return spikes