import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv 
from citywheels.llm import GeminiModel
from citywheels.prompts import SYSTEM_PROMPT
from citywheels.tools import TOOL_SCHEMAS

from eval.checks import check_answer
from eval.questions import QUESTIONS
from citywheels.agent import answer

RESULTS_PATH = Path(__file__).parent / "results.md"
PAUSE_SECONDS = 0

def run_questions(model, questions, pause=0):
    rows = []
    for number, question in enumerate(questions, start=1):
        tool_log = []
        started = time.time()
        try:
            answer_text = answer(model, [], question["question"], tool_log)
            problems = check_answer(question, answer_text, tool_log)
        except Exception as error:
            answer_text = ""
            problems = [f"error: {error}"]
 
        row = {
            "number": number,
            "question": question,
            "answer": answer_text,
            "problems": problems,
            "tools": [call["name"] for call in tool_log],
            "seconds": round(time.time() - started, 1),
        }
        rows.append(row)
 
        status = "PASS" if len(problems) == 0 else "FAIL"

        question_id = question["id"]
        seconds = row["seconds"]
        tools = row["tools"]
        message = f"[{status}] {question_id} ({seconds} s) tools: {tools}"
        print(message)
        
        for problem in problems:
            print("    -", problem)
        time.sleep(pause)
    return rows

def write_results(model_name, rows, path=RESULTS_PATH):

    passed = 0

    for row in rows:
        if len(row["problems"]) == 0:
            passed = passed + 1
 
    lines = []
    if not Path(path).exists():
        lines.append("# Eval results\n")
    lines.append(f"## Model: {model_name}, run {datetime.now():%Y-%m-%d %H:%M}\n")
    lines.append(f"**Passed: {passed} of {len(rows)}**\n")
    lines.append("| # | Question | Kind | Result | Tools called | Seconds |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for row in rows:
        if len(row["problems"]) == 0:
            result = "PASS"
        else:
            result = "FAIL"
        
        tools = ", ".join(row["tools"])
        if tools == "":
            tools = "-"

        question = row["question"]
        lines.append(f"| {row['number']} | {question['id']} | {question['kind']} | {result} | {tools} | {row['seconds']} |")
 
    failed = []

    for row in rows:
        if len(row["problems"]) > 0:
            failed.append(row)
    if failed:
        lines.append("\n### Failed questions\n")
        for row in failed:
            question_id = row["question"]["id"]
            question_text = row["question"]["question"]
            lines.append("**" + question_id + "**: " + question_text + "\n")

            for problem in row["problems"]:
                lines.append(f"- {problem}")
            lines.append(f"\nAnswer:\n\n```\n{row['answer']}\n```\n")
 
    with open(path, "a", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n\n")
    return passed

def main():
    load_dotenv()
    model = GeminiModel(SYSTEM_PROMPT, TOOL_SCHEMAS)
    print("Model:", model.model_name)
 
    rows = run_questions(model, QUESTIONS, pause=PAUSE_SECONDS)
    passed = write_results(model.model_name, rows)
    print(f"\nPassed {passed} of {len(rows)}. Results added to {RESULTS_PATH}")
 
 
if __name__ == "__main__":
    main()