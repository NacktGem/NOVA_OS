from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
import os
from datetime import datetime

from .database import SessionLocal, init_db
from .models import ThemePurchase, DMCAReport, ConsentLog


app = FastAPI(title="Black Rose API")

# Initialize database tables on startup
@app.on_event("startup")
def startup_event() -> None:
    init_db()


class ThemeSelection(BaseModel):
    theme: str


class PurchaseRequest(BaseModel):
    """
    Model representing a theme purchase request. Includes the theme
    name and an identifier for the user making the purchase. The user_id
    should be supplied by the authenticated client (e.g. extracted from
    a session or token) rather than hard-coded.
    """
    theme: str
    user_id: str


class DMCARequest(BaseModel):
    file_path: str
    user_id: str


class ConsentRequest(BaseModel):
    file_path: str
    model_id: str


ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "Black Rose Collective API"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/themes/select")
def select_theme(sel: ThemeSelection):
    # Persist to storage stub
    return {"selected": sel.theme}


@app.post("/payment/charge")
def payment(req: PurchaseRequest):
    provider = os.getenv("PAYMENT_PROVIDER_URL", "")
    return {"status": "processed", "theme": req.theme, "provider": provider}


@app.post("/admin/override")
def admin_override(sel: ThemeSelection, token: str = Header(..., alias="X-Admin-Token")):
    if token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"granted": sel.theme}


# New endpoint for theme purchases
@app.post("/purchase-theme")
def purchase_theme(req: PurchaseRequest, db=Depends(get_db)):
    """
    Purchase a theme by name.  Records the purchase in the database and returns a
    confirmation.  Integrate with a payment gateway as needed.
    """
    # Record the purchase with the provided user ID. In a production system,
    # user_id should be validated and derived from an authenticated session.
    purchase = ThemePurchase(theme=req.theme, user_id=req.user_id)
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    return {"status": "purchased", "theme": req.theme, "purchase_id": purchase.id}


# --- New Endpoints: Content Moderation and Consent Validation ---


@app.post("/dmca/check")
def dmca_check(request: DMCARequest, db=Depends(get_db)):
    """
    Check a file for potential DMCA violations.

    This endpoint delegates the check to the DMCA violation function
    defined in the Audita agent. In the stub implementation, it always
    returns no violation.

    Args:
        request: Contains file_path and user_id identifying the uploaded file.

    Returns:
        A dict containing violation status, method, details and timestamp.
    """
    # Import the DMCA checker from the consolidated novaos package.  The
    # legacy NovaOS_Core_Systems package is no longer used following the
    # repository restructure.  This import will raise ImportError if the
    # agents package is missing or misconfigured.
    from novaos.agents.audita.dmca_checker import check_dmca_violation
    result = check_dmca_violation(request.file_path, request.user_id)
    # Persist report
    report = DMCAReport(
        file_path=request.file_path,
        user_id=request.user_id,
        violation=result.get("violation", False),
        method=result.get("method"),
        details=result.get("details"),
        timestamp=datetime.fromisoformat(result.get("timestamp", datetime.utcnow().isoformat())),
        hash=result.get("hash"),
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    # Return original result
    return result


@app.post("/consent/validate")
def consent_validate(request: ConsentRequest, db=Depends(get_db)):
    """
    Validate an uploaded consent form.

    Args:
        request: Contains file_path and model_id identifying the form and model.

    Returns:
        A dict describing whether the consent form is valid and accompanying reason.
    """
    # Import the consent form validator from the novaos package.  The
    # legacy NovaOS_Core_Systems package is no longer used following the
    # repository restructure.  This import will raise ImportError if the
    # agents package is missing or misconfigured.
    from novaos.agents.audita.consent_upload import validate_consent_form
    result = validate_consent_form(request.file_path, request.model_id)
    # Persist log
    log = ConsentLog(
        file_path=request.file_path,
        model_id=request.model_id,
        valid=result.get("valid", False),
        reason=result.get("reason"),
        timestamp=datetime.fromisoformat(result.get("timestamp", datetime.utcnow().isoformat())),
        hash=result.get("hash"),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return result