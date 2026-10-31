import pytest
from citywheels.bookings import get_booking, load_bookings
 
 
def test_load_bookings_all_example_bookings():
    bookings = load_bookings()
    assert len(bookings) == 10
    assert "CW-1001" in bookings
 
 
def test_get_booking_found():
    result = get_booking("CW-1002")
    assert result["found"] == True
    assert result["booking"]["id"] == "CW-1002"
    assert result["booking"]["bike_type"] == "e-bike"
    assert result["booking"]["bikes"] == 2
 
 
@pytest.mark.parametrize("booking_id", ["cw-1002", "  CW-1002  ", "Cw-1002"])
def test_get_booking_ignores_case_AND_spaces(booking_id):
    result = get_booking(booking_id)
    assert result["found"] == True
    assert result["booking"]["id"] == "CW-1002"
 
 
def test_get_booking_not_found():
    result = get_booking("CW-9999")
    assert result["found"] == False
    assert result["booking_id"] == "CW-9999"
    assert "not found" in result["message"]
    assert "booking" not in result
 
  
@pytest.mark.parametrize("booking_id", ["", "   ", None, 1002])
def test_get_booking_bad_input_doesnt_crash(booking_id):
    result = get_booking(booking_id)
    assert result["found"] == False
    assert result["message"] == "No booking ID was given"
    assert "booking" not in result
 