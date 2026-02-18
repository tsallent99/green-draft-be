from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
import stripe
from app.config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
from app.database import get_db
from app.models import Entry
from app.models.entry import PaymentStatus

stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        entry_id = session.get("metadata", {}).get("entry_id")

        if entry_id:
            entry = db.query(Entry).filter(Entry.id == int(entry_id)).first()
            if entry:
                # Get the actual amount received after Stripe fees
                payment_intent_id = session.get("payment_intent")
                if payment_intent_id:
                    payment_intent = stripe.PaymentIntent.retrieve(
                        payment_intent_id,
                        expand=["latest_charge.balance_transaction"],
                    )
                    balance_transaction = payment_intent.latest_charge.balance_transaction
                    # net is in cents
                    entry.amount_paid = balance_transaction.net / 100
                entry.payment_status = PaymentStatus.PAID
                db.commit()

    return {"status": "ok"}
