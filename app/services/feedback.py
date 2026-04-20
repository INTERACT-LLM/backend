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
        "You are a Spanish language tutor who provides feedback on a student's messages, focusing on any language errors."
        "If there are any lanugage errors, you MUST set has_language_error to true AND provide corrected_text AND english_error_explanation. Please note that the english_error_explanation should be in English although citing the Spanish errors directly."
        "corrected_text and english_error_explanation must never be null when has_language_error is true. "
        "\n\nIMPORTANT: You must respond with valid JSON only, no additional text or explanations. "
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

def generate_general_feedback(messages: list[dict]):
    """
    From conversation history, generate structured feedback with positives and improvements.
    """
    formatted_conversation = "\n".join(
        f"{msg['role']}: {msg['content']}" for msg in messages
    )

    prompt = (
        "You are a helpful and encouraging Spanish language learning coach. "
        "The student has just finished a practice conversation. "
        "Review the conversation and provide feedback with:\n"
        "1. 'positive': A list of 2-3 specific things the student did well\n"
        "2. 'improvements': A list of 2-3 specific, actionable suggestions for improvement\n"
        "Keep the feedback concise and motivating.\n\n"
        f"Conversation Log:\n{formatted_conversation}\n\n"
        "IMPORTANT: Respond with valid JSON only, no additional text."
    )

    response = ollama.chat(
        model=FEEDBACK_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )


    return {"summary": response.message.content}