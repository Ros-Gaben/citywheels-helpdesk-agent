from citywheels.tools import run_tool

MAX_STEPS = 6
FALLBACK_REPLY = "Sorry, I could not finish this request. Please contact the staff"


class ModelReply:

    def __init__(self, text="", tool_calls = None, raw = None):
        self.text = text
        self.tool_calls = tool_calls or []
        self.raw = raw

def answer(model, history, user_text):
    history.append(model.user_message(user_text))

    for step in range(MAX_STEPS):
        reply = model.generate(history)
        history.append(reply.raw)

        if len(reply.tool_calls) == 0:
            return reply.text or FALLBACK_REPLY

        results = []
        for call in reply.tool_calls:
            result = run_tool(call["name"], call["args"])
            results.append((call["name"], result))
        history.append(model.tool_results_message(results))
    
    return FALLBACK_REPLY