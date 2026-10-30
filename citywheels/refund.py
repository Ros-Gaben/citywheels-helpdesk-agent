from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

NOW = datetime.fromisoformat("2026-06-10T09:00:00+02:00")
CENT = Decimal("0.01")


def _money(value) -> Decimal:
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)

def calculate_refund(booking: dict, now: datetime = NOW) -> dict:
    if booking["status"] != "confirmed":
        return {
            "booking_id": booking["id"],
            "can_cancel": False,
            "reason": f"Booking with status '{booking['status']}' cannot be cancelled.",
            "rental_refund_percent": 0,
            "rental_refund": _money(0),
            "booking_fee_refund": _money(0),
            "deposit_refund": _money(0),
            "total": _money(0),
            "method": None,
        }

    start = datetime.fromisoformat(booking["start"])
    time_left = start - now

    if time_left >= timedelta(hours=48):
        percent = 100
    elif time_left >= timedelta(hours=24):
        percent = 50
    else:
        percent = 0

    rental_refund = _money(_money(booking["rental_price_eur"]) * percent / 100)
    deposit_refund = _money(booking["deposit_eur"])
    booking_fee_refund = _money(0)


    return {
        "booking_id": booking["id"],
        "can_cancel": True,
        "reason": None,
        "hours_before_start": round(time_left.total_seconds() / 3600, 2),
        "rental_refund_percent": percent,
        "rental_refund": rental_refund,
        "booking_fee_refund": booking_fee_refund,
        "deposit_refund": deposit_refund,
        "total": rental_refund + booking_fee_refund + deposit_refund,
        "method": "voucher" if booking["paid_with"] == "voucher" else "card",
    }
