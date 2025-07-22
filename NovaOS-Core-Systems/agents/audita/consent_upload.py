

import os
import json
import re
import hashlib
from datetime import datetime
from pathlib import Path

from config.audit_logger import log_event
from tools.ocr_scanner import extract_text_from_pdf
from tools.id_verifier import match_id_metadata
from vault.identity_chain import fetch_model_release_record


def validate_consent_form(file_path: str, model_id: str) -> dict:
    """
    Validates a consent form for multi-model content uploads.
    Checks include: file presence, OCR content extraction, ID metadata validation, release form matching.
    
    Args:
        file_path (str): Path to the uploaded consent form (PDF).
        model_id (str): Unique identifier of the collaborating model.

    Returns:
        dict: {
            "valid": bool,
            "reason": str,
            "timestamp": ISO timestamp,
            "hash": SHA256 of file,
        }
    """
    result = {
        "valid": False,
        "reason": "",
        "timestamp": datetime.utcnow().isoformat(),
        "hash": "",
    }

    if not os.path.isfile(file_path):
        result["reason"] = "Consent form not found."
        return result

    try:
        # Step 1: Extract text from form (PDF → text)
        extracted_text = extract_text_from_pdf(file_path)

        if not extracted_text or len(extracted_text) < 100:
            result["reason"] = "OCR scan failed or content too short."
            return result

        # Step 2: Verify required fields in text
        required_fields = ["Full Legal Name", "Date of Birth", "Signature", "Date", "Grant of Consent"]
        missing_fields = [field for field in required_fields if field.lower() not in extracted_text.lower()]

        if missing_fields:
            result["reason"] = f"Missing required fields: {', '.join(missing_fields)}"
            return result

        # Step 3: Validate metadata against model release vault
        form_metadata = {
            "name": _extract_name(extracted_text),
            "dob": _extract_dob(extracted_text),
            "signed": _extract_signature(extracted_text),
        }

        if not all(form_metadata.values()):
            result["reason"] = "Essential metadata missing in form."
            return result

        # Step 4: Retrieve stored release info from vault
        vault_record = fetch_model_release_record(model_id)

        if not vault_record:
            result["reason"] = "No model release record found in vault."
            return result

        if not match_id_metadata(form_metadata, vault_record):
            result["reason"] = "Metadata mismatch with registered ID."
            return result

        # Step 5: Hash form for log and audit
        with open(file_path, "rb") as f:
            raw_data = f.read()
            result["hash"] = hashlib.sha256(raw_data).hexdigest()

        result["valid"] = True
        result["reason"] = "Consent form validated."

        log_event("consent_validation_passed", {
            "model_id": model_id,
            "form_hash": result["hash"],
            "timestamp": result["timestamp"]
        })

    except Exception as e:
        result["reason"] = f"Validation error: {str(e)}"
        log_event("consent_validation_failed", {
            "model_id": model_id,
            "error": str(e),
            "timestamp": result["timestamp"]
        })

    return result


def _extract_name(text: str) -> str:
    match = re.search(r"Full Legal Name[:\s]+([A-Z][a-z]+\s[A-Z][a-z]+)", text)
    return match.group(1) if match else ""


def _extract_dob(text: str) -> str:
    match = re.search(r"Date of Birth[:\s]+(\d{2}/\d{2}/\d{4})", text)
    return match.group(1) if match else ""


def _extract_signature(text: str) -> str:
    match = re.search(r"Signature[:\s]+([A-Z][a-z]+\s[A-Z][a-z]+)", text)
    return match.group(1) if match else ""