

"""
Echo Agent — Flag Escalator Module
Aggregates flagged content from multiple sources and routes it to moderation or Nova.
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
from config.audit_logger import log_event
from typing import List, Dict

# Paths to watch for flagged data
BASE_DIR = Path(__file__).resolve().parents[3]
LOG_DIR = BASE_DIR / "logs"
ESCALATION_LOG = LOG_DIR / "echo" / "escalated_flags.parquet"

# Flag types to ingest
FLAG_SOURCES = {
    "sentiment": LOG_DIR / "echo" / "sentiment_log.parquet",
    "dmca": LOG_DIR / "audita" / "dmca_flags.parquet",
    "consent": LOG_DIR / "audita" / "consent_flags.parquet",
    "chat": LOG_DIR / "chat" / "flagged_messages.parquet"
}


def load_flags(source: Path, label: str) -> pd.DataFrame:
    if not source.exists():
        return pd.DataFrame()

    df = pd.read_parquet(source)
    df["source"] = label
    return df


def escalate_flags(window: int = 10) -> List[Dict]:
    """
    Collects recent flags across all subsystems and identifies priority escalations.

    Args:
        window (int): How many recent entries per source to evaluate.

    Returns:
        List[Dict]: List of escalated entries for moderation or Nova review.
    """
    escalated = []
    for label, path in FLAG_SOURCES.items():
        df = load_flags(path, label)
        if df.empty:
            continue

        recent = df.tail(window)
        for _, row in recent.iterrows():
            entry = row.to_dict()
            entry["escalated_at"] = datetime.utcnow().isoformat()
            entry["priority"] = _assign_priority(entry)
            escalated.append(entry)
            log_event("flag_escalated", entry)

    if escalated:
        _write_escalations(escalated)

    return escalated


def _assign_priority(entry: Dict) -> str:
    """
    Assigns escalation priority based on content and source.

    Args:
        entry (dict): Flagged entry data.

    Returns:
        str: Priority level.
    """
    if entry["source"] == "sentiment" and abs(entry.get("polarity", 0)) > 0.85:
        return "high"
    if entry["source"] == "dmca":
        return "high"
    if entry["source"] == "consent":
        return "critical"
    if entry["source"] == "chat" and "violence" in entry.get("details", "").lower():
        return "critical"
    return "normal"


def _write_escalations(data: List[Dict]):
    """
    Stores escalated flag entries persistently.

    Args:
        data (List[Dict]): Escalated entries.
    """
    ESCALATION_LOG.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(data)
    if ESCALATION_LOG.exists():
        old = pd.read_parquet(ESCALATION_LOG)
        df = pd.concat([old, df], ignore_index=True)
    df.to_parquet(ESCALATION_LOG, index=False)