def check_answer(question, answer_text, tool_log):
    problems = []
    text = answer_text.lower()
    tool_names = [call["name"] for call in tool_log]
 
    expected = question.get("expect_tool")
    
    if expected:
        if isinstance(expected, str):
            expected = [expected]
        if not any(name in tool_names for name in expected):
            problems.append(f"None of the tools {expected} was called| (called: {tool_names})")


 
    for word in question.get("contains", []):
        if word.lower() not in text:
            problems.append(f"Answer does not contain: '{word}'")


 
    any_words = question.get("contains_any", [])
    if any_words:
        found = False
        for word in any_words:
            if word.lower() in text:
                found = True
        if not found:
            problems.append(f"Answer contains none of: {any_words}")


 
    for word in question.get("not_contains", []):
        if word.lower() in text:
            problems.append(f"Answer contains forbidden: '{word}'")
 
    return problems
 