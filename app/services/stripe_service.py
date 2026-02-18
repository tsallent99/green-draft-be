import stripe
from app.config import STRIPE_SECRET_KEY, FRONTEND_URL

stripe.api_key = STRIPE_SECRET_KEY


def create_checkout_session(entry_id: int, entry_fee: float, league_name: str, league_id: int) -> str:
    """Create a Stripe Checkout Session and return the checkout URL."""
    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "eur",
                    "unit_amount": int(entry_fee * 100),
                    "product_data": {
                        "name": f"Entry fee - {league_name}",
                    },
                },
                "quantity": 1,
            }
        ],
        metadata={"entry_id": str(entry_id)},
        success_url=f"{FRONTEND_URL}/your-leagues/{league_id}",
        cancel_url=f"{FRONTEND_URL}/payment/cancel",
    )
    return session.url
