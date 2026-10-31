import json
 
from citywheels.tools import TOOL_FUNCTIONS, TOOL_SCHEMAS, calculate_refund, run_tool

def test_calculate_refund_tool():
    result = calculate_refund("CW-1002")
    assert result["can_cancel"] is True
    assert result["total"] == "340.00"
    assert result["method"] == "card"
    assert result["currency"] == "EUR"


def test_calculate_refund_result_turned_into_json():
    result = calculate_refund("CW-1002")
    json.dumps(result)

def test_calculate_refund_unknown_booking():
    result = calculate_refund("CW-9999")
    assert result["found"] == False




def test_calculate_refund_with_other_time():
    result = calculate_refund("CW-1002", cancel_at="2026-06-11T17:00:00+02:00")
    assert result["rental_refund_percent"] == 0
    assert result["total"] == "300.00"


def test_calculate_refund_cancel_at_without_timezone():
    result = calculate_refund("CW-1002", cancel_at="2026-06-11T17:00:00")
    assert result["rental_refund_percent"] == 0
 
 
def test_calculate_refund_bad_cancel_at():
    result = calculate_refund("CW-1002", cancel_at="tomorrow")
    assert "error" in result
 
 
def test_run_tool_calls_right_function():
    result = run_tool("get_booking", {"booking_id": "CW-1001"})
    assert result["found"] == True
 
 
def test_run_tool_unknown_tool():
    result = run_tool("delete_everything", {})
    assert "error" in result
 
 
def test_run_tool_wrong_arguments_doesnt_crash():
    result = run_tool("get_booking", {"wrong_name": 1})
    assert "error" in result
 
 
def test_every_schema_has_a_function():
    for schema in TOOL_SCHEMAS:
        assert schema["name"] in TOOL_FUNCTIONS
    assert len(TOOL_SCHEMAS) == len(TOOL_FUNCTIONS)