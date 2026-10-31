import json
from pathlib import Path

BOOKINGS_PATH = Path(__file__).parent.parent / "data" / "bookings.json"


def load_bookings(path = BOOKINGS_PATH):
    bookings = json.loads(Path(path).read_text(encoding="utf-8"))
    
    return {
        booking["id"]: booking
        for booking in bookings
    }

def get_booking(booking_id, path = BOOKINGS_PATH):
    if not isinstance(booking_id, str) or not booking_id.strip():
        return {
            "found": False,
            "booking_id": booking_id,
            "message": "No booking ID was given",
        }

    booking_id = booking_id.strip().upper()
    bookings = load_bookings(path)

    if booking_id not in bookings:
        return {
            "found": False,
            "booking_id": booking_id,
            "message": f"Booking with ID '{booking_id}' was not found",
        }
    return {
        "found": True,
        "booking": bookings[booking_id],}