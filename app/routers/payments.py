from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
import stripe
import logging
from app.config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
from app.database import get_db
from app.models import Entry
from app.models.entry import PaymentStatus

stripe.api_key = STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)

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

    event_type = event["type"]

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        entry_id = session.get("metadata", {}).get("entry_id")

        if entry_id:
            entry = db.query(Entry).filter(Entry.id == int(entry_id)).first()
            if entry:
                entry.payment_status = PaymentStatus.PAID
                db.commit()
                logger.info(f"Entry {entry_id}: payment_status set to PAID")

    elif event_type == "charge.updated":
        # balance_transaction is available at this point
        charge = event["data"]["object"]
        payment_intent_id = charge.get("payment_intent")

        if payment_intent_id and charge.get("balance_transaction"):
            # Find the entry via the checkout session metadata
            sessions = stripe.checkout.Session.list(payment_intent=payment_intent_id, limit=1)
            if sessions.data:
                entry_id = sessions.data[0].metadata.get("entry_id")
                if entry_id:
                    entry = db.query(Entry).filter(Entry.id == int(entry_id)).first()
                    if entry:
                        bt = stripe.BalanceTransaction.retrieve(charge["balance_transaction"])
                        entry.amount_paid = bt.net / 100
                        db.commit()
                        logger.info(f"Entry {entry_id}: amount_paid set to {entry.amount_paid}")

    return {"status": "ok"}
