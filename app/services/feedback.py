"""
Feedback service (seperate API call from chat endpoint)

Structured feedback response based on https://docs.ollama.com/capabilities/structured-outputs#python-2
-> Note: Ollama recommends passing JSON schema as prompt + in the chat call
"""
import ollama
from app.models.feedback import FeedbackResponse

FEEDBACK_MODEL = "qwen3.5:2b"

def generate_immediate_feedback(
    last_user_message: dict,
):
    prompt = (
        "You are a helpful and precise language tutor. "
        "Analyse the student's message for errors in grammar, vocabulary, or usage. "
        "If there are errors, provide a corrected version and a brief explanation. "
        "If there are no errors, set has_error to false and leave other fields null. "
        "Respond in this JSON format: "
        "{}"
    ).format(FeedbackResponse.model_json_schema())

    response = ollama.chat(
        model=FEEDBACK_MODEL,
        messages=[{"role": "system", "content": prompt}] + [last_user_message],
        format=FeedbackResponse.model_json_schema()
    )

    try:
        feedback = FeedbackResponse.model_validate_json(response.message.content)
        feedback_status = "success"
    except Exception as e:
        return {"FeedbackResponse": None, "feedback_status": "error", "detail": str(e)}

    return {"FeedbackResponse": feedback, "feedback_status": feedback_status}