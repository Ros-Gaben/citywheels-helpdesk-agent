import json
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
 
import pytest
 
from citywheels.refund import NOW, calculate_refund
Data = Path(__file__).parent.parent / "data" / "bookings.json"

BOOKINGS = {}

for booking in json.loads(Data.read_text(encoding="utf-8")):
    BOOKINGS[booking["id"]] = booking

@pytest.mark.parametrize(
    "booking_id, expected_total, expected_method",[
        ("CW-1001", "90", "card"),
        ("CW-1002", "340", "card"),
        ("CW-1003", "50", "card"),
        ("CW-1004", "73", "voucher"),
        ("CW-1007", "186", "card"),
        ("CW-1009", "169", "card"),
        ("CW-1010", "170", "card"), ], 
)
def test_calculate_total_and_method(booking_id, expected_total, expected_method):
    result = calculate_refund(BOOKINGS[booking_id])
    assert result["can_cancel"] == True
    assert result["total"] == Decimal(expected_total)
    assert result["method"] == expected_method



@pytest.mark.parametrize("booking_id", ["CW-1005", "CW-1006", "CW-1008"])
def test_cannot_cancel_not_confirmed(booking_id):
    result = calculate_refund(BOOKINGS[booking_id])
    assert result["can_cancel"] == False
    assert result["total"] == Decimal("0")
    assert result["method"] == None

def test_percentages_outside_boundaries():  
    assert calculate_refund(BOOKINGS["CW-1001"])["rental_refund_percent"] == 100
    assert calculate_refund(BOOKINGS["CW-1002"])["rental_refund_percent"] == 50
    assert calculate_refund(BOOKINGS["CW-1003"])["rental_refund_percent"] == 0

def test_percentages_at_boundaries():
    assert calculate_refund(BOOKINGS["CW-1007"])["rental_refund_percent"] == 100
    assert calculate_refund(BOOKINGS["CW-1010"])["rental_refund_percent"] == 50


def test_1_minute_before_48_hours():
    booking = BOOKINGS["CW-1001"].copy()
    start_time = NOW + timedelta(hours=47, minutes=59)

    booking["start"] = start_time.isoformat()
    result = calculate_refund(booking)
    assert result["rental_refund_percent"] == 50

def test_1_minute_before_24_hours():
    booking = BOOKINGS["CW-1001"].copy()
    start_time = NOW + timedelta(hours=23, minutes=59)

    booking["start"] = start_time.isoformat()
    result = calculate_refund(booking)
    assert result["rental_refund_percent"] == 0


def test_booking_fee_never_refunded():
    result = calculate_refund(BOOKINGS["CW-1001"])
    assert result["booking_fee_refund"] == Decimal("0")

def test_deposit_is_not_multiplied_by_number_of_bikes():
    assert calculate_refund(BOOKINGS["CW-1002"])["deposit_refund"] == Decimal("300")
