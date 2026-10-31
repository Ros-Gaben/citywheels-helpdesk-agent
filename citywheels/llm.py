import os
import time
 
from google import genai
from google.genai import errors, types

from citywheels.agent import ModelReply

DEFAULT_MODEL = "gemini-flash-lite-latest"
RETRY_CODES = (429, 500, 503)
MIN_REQUEST_INTERVAL = 4.2


class GeminiModel:
    def __init__(self, system_prompt, tool_schemas):
        self.client = genai.Client() 
        self.model_name = os.getenv("LLM_MODEL", DEFAULT_MODEL)
        self.last_request_time = None
        self.config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=[types.Tool(function_declarations=tool_schemas)],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
 
    def user_message(self, text):
        return types.Content(role="user", parts=[types.Part(text=text)])
 
    def tool_results_message(self, results):
        parts = []
        for name, result in results:
            parts.append(types.Part.from_function_response(name=name, response={"result": result}))
        return types.Content(role="user", parts=parts)
 
    def generate(self, history):
        response = self._call_api(history)
 
        if not response.candidates or response.candidates[0].content is None:
            text = "Sorry, I cannot answer this. Please contact the staff."
            return ModelReply(text=text, raw=types.Content(role="model", parts=[types.Part(text=text)]))
 
        content = response.candidates[0].content
        text = ""
        tool_calls = []
        for part in content.parts or []:
            if part.function_call:
                tool_calls.append({
                    "name": part.function_call.name,
                    "args": dict(part.function_call.args or {}),
                })
            elif part.text:
                text += part.text
        return ModelReply(text=text, tool_calls=tool_calls, raw=content)
 
    def _call_api(self, history):
        for attempt in range(3):
            if self.last_request_time is not None:
                elapsed = time.monotonic() - self.last_request_time
                wait = MIN_REQUEST_INTERVAL - elapsed
                if wait > 0:
                    time.sleep(wait)

            self.last_request_time = time.monotonic()
            try:
                return self.client.models.generate_content(
                    model=self.model_name, contents=history, config=self.config
                )
            except errors.APIError as error:
                if getattr(error, "code", None) in RETRY_CODES and attempt < 2:
                    time.sleep(5 * (attempt + 1))
                else:
                    raise
 