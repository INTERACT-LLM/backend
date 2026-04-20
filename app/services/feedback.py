"""
Feedback service (seperate API call from chat endpoint)

Structured feedback response based on https://docs.ollama.com/capabilities/structured-outputs#python-2
-> Note: Ollama recommends passing JSON schema as prompt + in the chat call
"""
import ollama
from app.models.feedback import FeedbackResponse

from app.services.model_config import MODEL as FEEDBACK_MODEL

def generate_immediate_feedback(
    last_user_message: dict,
):
    schema = FeedbackResponse.model_json_schema()
    
    prompt = (
        "You are a Spanish language tutor who provides feedback on a student's messages. Analyse the student's message for errors in grammar, vocabulary, usage, spelling, punctuation, or any other language mistakes."
        "If there are errors, you MUST set has_error to true AND provide corrected_text AND english_error_explanation. Please note that the english_error_explanation should be in English although citing the Spanish errors directly."
        "corrected_text and english_error_explanation must never be null when has_error is true. "
        "\n\nIMPORTANT: You must respond with valid JSON only, no additional text or explanations. "
        "The JSON response must follow this exact format:\n"
        f"{schema}"
        "\n\nRespond with JSON only:"
    )

    response = ollama.chat(
        model=FEEDBACK_MODEL,
        messages=[{"role": "system", "content": prompt}] + [last_user_message],
        format=schema
    )

    try:
        feedback = FeedbackResponse.model_validate_json(response.message.content)
        feedback_status = "success"
    except Exception as e:
        return {"FeedbackResponse": None, "feedback_status": "error", "detail": str(e)}

    return {"FeedbackResponse": feedback, "feedback_status": feedback_status}