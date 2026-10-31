from citywheels.agent import ModelReply
from eval.checks import check_answer
from eval.questions import QUESTIONS
from eval.run_eval import run_questions

 
def test_check_answer_passes_when_everything_is_ok():
    question = {"expect_tool": "calculate_refund", "contains": ["340"]}
    tool_log = [{"name": "calculate_refund", "args": {}, "result": {}}]
    assert check_answer(question, "You get 340.00 EUR", tool_log) == []
 
 
def test_check_answer_fails_if_tool_was_not_called():
    question = {"expect_tool": "calculate_refund", "contains": ["340"]}
    problems = check_answer(question, "You get 340.00 EUR", [])
    assert len(problems) == 1
 
 
def test_check_answer_expect_tool_can_be_a_list():
    question = {"expect_tool": ["get_booking", "calculate_refund"]}
    tool_log = [{"name": "get_booking", "args": {}, "result": {}}]
    assert check_answer(question, "text", tool_log) == []
 
 
def test_check_answer_contains_and_contains_any():
    question = {"contains": ["voucher"], "contains_any": ["cannot", "unable"]}
    assert check_answer(question, "Refund as a VOUCHER, you are unable to get cash", []) == []
    assert len(check_answer(question, "Something else", [])) == 2
 
 
def test_check_answer_not_contains_ignores_case():
    question = {"not_contains": ["Canberra"]}
    assert len(check_answer(question, "The capital is canberra", [])) == 1
    assert check_answer(question, "I can only help with bike rental", []) == []

 
def test_questions_meet_the_requirements():
    kinds = [question["kind"] for question in QUESTIONS]
    assert len(QUESTIONS) >= 10
    assert kinds.count("refund") >= 2
    assert kinds.count("refuse") >= 2
 
 
def test_question_ids_are_unique():
    ids = [question["id"] for question in QUESTIONS]
    assert len(ids) == len(set(ids))

 
class ScriptedModel:
    def __init__(self, replies):
        self.replies = list(replies)
 
    def user_message(self, text):
        return {"role": "user", "text": text}
 
    def tool_results_message(self, results):
        return {"role": "tool", "results": results}
 
    def generate(self, history):
        return self.replies.pop(0)
 
 
def test_run_questions_marks_pass_and_fail():
    questions = [
        {"id": "refund", "kind": "refund", "question": "Cancel CW-1002",
         "expect_tool": "calculate_refund", "contains": ["340"]},
        {"id": "capital", "kind": "refuse", "question": "Capital of Australia?",
         "not_contains": ["Canberra"]},
    ]
    call = ModelReply(tool_calls=[{"name": "calculate_refund", "args": {"booking_id": "CW-1002"}}],
                      raw={"role": "model"})
    model = ScriptedModel([
        call,
        ModelReply(text="You get 340.00 EUR", raw={"role": "model"}),
        ModelReply(text="It is Canberra", raw={"role": "model"}),
    ])
    rows = run_questions(model, questions)
    assert rows[0]["problems"] == []
    assert rows[0]["tools"] == ["calculate_refund"]
    assert len(rows[1]["problems"]) == 1