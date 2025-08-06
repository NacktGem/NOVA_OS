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
    Request model used when purchasing a theme.  A user identifier is
    included so that purchases can be associated with the correct user.  In a
    production deployment this would likely correspond to a session or JWT
    subject rather than a free‑form string.
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

# Import theme definitions.  These are defined in a separate module so that
# the frontend and backend can share a single source of truth.
from .themes import ALL_THEMES  # noqa: E402  # import placed after class definitions

from typing import List, Optional  # noqa: E402  # unify type hints

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
    # Record the purchase in the database
    # Record the purchase with the provided user identifier.  In the future, this
    # could be extracted from a session or authentication token rather than
    # supplied directly by the client.
    purchase = ThemePurchase(theme=req.theme, user_id=req.user_id)
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    return {"status": "purchased", "theme": req.theme, "purchase_id": purchase.id}

# ---------------------------------------------------------------------------
#  Additional Endpoints
#
#  The following endpoints expose core platform data such as available
#  themes and moderation logs.  They are intentionally simple; if you need
#  pagination, filtering or authentication, those enhancements can be added
#  later.


class ThemeResponse(BaseModel):
    """Schema representing a theme and its associated colours."""
    name: str
    colors: List[str]


class DMCARecord(BaseModel):
    """Schema representing a stored DMCA report."""
    id: int
    file_path: str
    user_id: str
    violation: bool
    method: Optional[str] = None
    details: Optional[str] = None
    timestamp: datetime
    hash: Optional[str] = None

    class Config:
        orm_mode = True


class ConsentRecord(BaseModel):
    """Schema representing a stored consent log entry."""
    id: int
    file_path: str
    model_id: str
    valid: bool
    reason: Optional[str] = None
    timestamp: datetime
    hash: Optional[str] = None

    class Config:
        orm_mode = True


@app.get("/themes", response_model=List[ThemeResponse])
def list_themes() -> List[ThemeResponse]:
    """
    Return the list of available themes.

    The themes are defined in :mod:`backend.themes` and contain a name and
    colour palette.  Clients can use this endpoint to present purchase
    options or previews without hard‑coding theme data in the frontend.
    """
    return [ThemeResponse(**t) for t in ALL_THEMES]


@app.get("/dmca/reports", response_model=List[DMCARecord])
def get_dmca_reports(limit: int = 100, db=Depends(get_db)) -> List[DMCARecord]:
    """
    Retrieve the most recent DMCA reports.

    Args:
        limit: Maximum number of records to return.
        db: Injected database session.

    Returns:
        A list of DMCA reports ordered by descending timestamp.
    """
    records = db.query(DMCAReport).order_by(DMCAReport.timestamp.desc()).limit(limit).all()
    return records


@app.get("/consent/logs", response_model=List[ConsentRecord])
def get_consent_logs(limit: int = 100, db=Depends(get_db)) -> List[ConsentRecord]:
    """
    Retrieve the most recent consent validation logs.

    Args:
        limit: Maximum number of records to return.
        db: Injected database session.

    Returns:
        A list of consent logs ordered by descending timestamp.
    """
    logs = db.query(ConsentLog).order_by(ConsentLog.timestamp.desc()).limit(limit).all()
    return logs


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
    try:
        from NovaOS_Core_Systems.agents.audita.dmca_checker import check_dmca_violation  # type: ignore
    except Exception:
        # Fallback import when package name contains hyphens.
        from NovaOS_Core_Systems.agents.audita.dmca_checker import check_dmca_violation  # pragma: no cover
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
    try:
        from NovaOS_Core_Systems.agents.audita.consent_upload import validate_consent_form  # type: ignore
    except Exception:
        from NovaOS_Core_Systems.agents.audita.consent_upload import validate_consent_form  # pragma: no cover
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