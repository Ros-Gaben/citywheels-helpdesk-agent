from citywheels.agent import FALLBACK_REPLY, MAX_STEPS, ModelReply, answer
from citywheels.prompts import SYSTEM_PROMPT

class FakeModel:
    def __init__(self, replies):
        self.replies = list(replies)
        self.history_sizes = [] 
 
    def user_message(self, text):
        return {"role": "user", "text": text}
 
    def tool_results_message(self, results):
        return {"role": "tool", "results": results}
 
    def generate(self, history):
        self.history_sizes.append(len(history))
        return self.replies.pop(0)
 
 
def text_reply(text):
    return ModelReply(text=text, raw={"role": "model", "text": text})
 
 
def tool_reply(name, args):
    return ModelReply(tool_calls=[{"name": name, "args": args}], raw={"role": "model", "call": name})
 
 
def test_answer_without_tools():
    model = FakeModel([text_reply("Hello!")])
    history = []
    assert answer(model, history, "Hi") == "Hello!"
    assert len(history) == 2  
 
def test_answer_with_tool_call():
    model = FakeModel([
        tool_reply("calculate_refund", {"booking_id": "CW-1002"}),
        text_reply("You will get back 340.00 EUR"),
    ])
    history = []
    result = answer(model, history, "I want to cancel CW-1002. How much do I get back?")
    assert result == "You will get back 340.00 EUR"
 
    assert len(history) == 4
    tool_name, tool_result = history[2]["results"][0]
    assert tool_name == "calculate_refund"
    assert tool_result["total"] == "340.00"
 
 
def test_unknown_tool_does_not_crash_the_agent():
    model = FakeModel([
        tool_reply("delete_everything", {}),
        text_reply("Sorry, I can't do that"),
    ])
    history = []
    assert answer(model, history, "Delete everything") == "Sorry, I can't do that"
    assert "error" in history[2]["results"][0][1]
 
 
def test_agent_stops_if_model_loops_forever():
    model = FakeModel([tool_reply("get_booking", {"booking_id": "CW-1001"})] * MAX_STEPS)
    assert answer(model, [], "Hello") == FALLBACK_REPLY
    assert len(model.history_sizes) == MAX_STEPS
 
 
def test_history_is_kept_between_questions():
    model = FakeModel([text_reply("First answer"), text_reply("Second answer")])
    history = []
    answer(model, history, "First question")
    answer(model, history, "Second question")
 
    assert model.history_sizes == [1, 3]
 
 
def test_system_prompt_has_current_date():
    assert "2026-06-10" in SYSTEM_PROMPT

def test_tool_log_records_tool_calls():
    model = FakeModel([
        tool_reply("calculate_refund", {"booking_id": "CW-1002"}),
        text_reply("You will get back 340.00 EUR"),
    ])
    
    tool_log = []
    answer(model, [], "Cancel CW-1002", tool_log)
    assert len(tool_log) == 1
    assert tool_log[0]["name"] == "calculate_refund"
    assert tool_log[0]["result"]["total"] == "340.00"