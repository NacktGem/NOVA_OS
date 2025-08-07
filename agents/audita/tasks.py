"""
Audita Task Runner – Handles legal compliance, DMCA checks, policy audits, and consent tracking.
Integrates offline GGUF LLMs for reasoning and reporting, and connects to internal vault and logging systems.
"""

from .model_loader import generate
from agents.audita.dmca_checker import check_dmca_violation
from agents.audita.consent_upload import validate_consent_form
from core.vault import get_vault_record
from utils.logging import log_event
from datetime import datetime

def run_audit(prompt: str, max_tokens: int = 512, temperature: float = 0.4) -> str:
    """Run a general audit prompt using the local GGUF model."""
    log_event("audita.audit_prompt_run", {"timestamp": datetime.now().isoformat(), "prompt": prompt})
    return generate(prompt, max_tokens=max_tokens, temperature=temperature)

def run_dmca_scan(content_path: str) -> dict:
    """Run a DMCA violation scan on submitted content."""
    result = check_dmca_violation(content_path)
    log_event("audita.dmca_scan", {"file": content_path, "result": result})
    return result

def verify_consent(form_path: str, user_id: str) -> dict:
    """Validate a submitted model release or consent form."""
    result = validate_consent_form(form_path)
    log_event("audita.consent_check", {"user_id": user_id, "form_path": form_path, "result": result})
    return result

def retrieve_legal_record(vault_key: str) -> dict:
    """Access encrypted legal document or release from vault."""
    record = get_vault_record(vault_key)
    log_event("audita.vault_access", {"vault_key": vault_key, "accessed_at": datetime.now().isoformat()})
    return record
