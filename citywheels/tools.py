from datetime import datetime
from decimal import Decimal

from citywheels import refund
from citywheels.bookings import get_booking
from citywheels.policies import search_policies

def calculate_refund(booking_id, cancel_at = None):
    found = get_booking(booking_id)
    if not found["found"]:
        return found

    now = refund.NOW
    if cancel_at:
        try:
            now = datetime.fromisoformat(cancel_at)
        except ValueError:
            return {
                "error": "cancel_at must look like 2026-06-11T10:00:00+02:0"
            }

        if now.tzinfo == None:
            now = now.replace(tzinfo=refund.NOW.tzinfo)

    result = refund.calculate_refund(found["booking"], now)
    answer = {}

    for key, value in result.items():
        if isinstance(value, Decimal):
            value = str(value)
        answer[key] = value
    answer["currency"] = "EUR"
    return answer


TOOL_FUNCTIONS = {
    "search_policies": search_policies,
    "get_booking": get_booking,
    "calculate_refund": calculate_refund,
}

TOOL_SCHEMAS = [
    {
        "name": "search_policies",
        "description": (
            "Search the CityWheels rules: prices, opening hours, cancellation and refund rules, "
            "age limits, FAQ. Returns the most relevant sections. "
            "Use short English keywords, even if the customer writes in another language."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Short English keywords, for example: opening hours saturday",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_booking",
        "description": (
            "Get the details of one booking by its number (for example CW-1002): "
            "status, bike type, start and end time, prices, deposit and how it was paid."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "booking_id": {
                    "type": "string",
                    "description": "Booking number, for example CW-1002",
                },
            },
            "required": ["booking_id"],
        },
    },
    {
        "name": "calculate_refund",
        "description": (
            "Calculate exactly how much money the customer gets back if they cancel a booking. "
            "ALWAYS use this tool for any refund amount, never calculate refunds yourself. "
            "By default it assumes the booking is cancelled now. "
            "Use cancel_at only if the customer asks about cancelling at another time."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "booking_id": {
                    "type": "string",
                    "description": "Booking number, for example CW-1002",
                },
                "cancel_at": {
                    "type": "string",
                    "description": "Optional. Cancellation time, for example 2026-06-11T10:00:00+02:00",
                },
            },
            "required": ["booking_id"],
        },
    },
]


def run_tool(name, arguments):

    if name not in TOOL_FUNCTIONS:
        return {"error": f"Unknown tool '{name}'"}
    try:
        return TOOL_FUNCTIONS[name](**(arguments or {}))
    except Exception as error:
        return {"error": f"Tool '{name}' failed: {error}"}