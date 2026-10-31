from dotenv import load_dotenv
 
from citywheels.agent import answer
from citywheels.llm import GeminiModel
from citywheels.prompts import SYSTEM_PROMPT
from citywheels.tools import TOOL_SCHEMAS


def main():
    load_dotenv()
    model = GeminiModel(SYSTEM_PROMPT, TOOL_SCHEMAS)
    history = []

    print("CityWheels support. Type 'exit' to quit ")
    while True:
        user_text = input("You: ").strip()
        if user_text.lower() in ("exit", "quit"):
            break
        if user_text == "":
            continue
 
        size_before = len(history)
        tool_log = []
        try:
            reply = answer(model, history, user_text, tool_log)
        except Exception as error:
            del history[size_before:]
            reply = f"Sorry, something went wrong ({error}). Please try again."

        for call in tool_log:
            name = call["name"]
            args = call["args"]
            result = str(call["result"])[:400]
            print(f"  [tool] {name}({args}) -> {result}")
        print("Agent:", reply)
 
 
if __name__ == "__main__":
    main()