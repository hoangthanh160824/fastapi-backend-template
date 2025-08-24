from fastapi import APIRouter, Depends, HTTPException
from pydantic.networks import EmailStr
from sqlmodel import Session, select, text

from app.api.deps import get_current_active_superuser
from app.core.db import engine
from app.models import Message
from app.utils import generate_test_email, send_email

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")


@router.get("/health-check/")
async def health_check() -> bool:
    """
    Health check endpoint that verifies database connectivity.
    """
    try:
        # Test database connection
        with Session(engine) as session:
            # Simple query to test connection
            session.exec(text("SELECT 1"))
        return True
    except Exception as e:
        # Return False instead of raising exception for health check
        return False
