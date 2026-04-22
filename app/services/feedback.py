"""
Feedback service (seperate API call from chat endpoint)

Structured feedback response based on https://docs.ollama.com/capabilities/structured-outputs#python-2
-> Note: Ollama recommends passing JSON schema as prompt + in the chat call
"""
import re
import ollama
from app.models.feedback import FeedbackResponse, GeneralFeedbackResponse

from app.services.model_config import MODEL as FEEDBACK_MODEL

def generate_immediate_feedback(
    last_user_message: dict,
):
    schema = FeedbackResponse.model_json_schema()
    
    prompt = (
        "You are a Spanish language tutor who provides feedback on a student's messages, focusing on any language errors."
        "If there are any lanugage errors, you MUST set has_language_error to true AND provide corrected_text AND english_error_explanation. Please note that the english_error_explanation should be in English although citing the Spanish errors directly."
        "corrected_text and english_error_explanation must never be null when has_language_error is true. "

        "EXAMPLE FEEDBACK RESPONSE (in JSON format):\n"
        "{\n"
        "  \"has_language_error\": true,\n"
        "  \"corrected_text\": \"Me llamo Antonio\",\n"
        "  \"english_error_explanation\": \"You used the verb form 'llames' in 'Me llames Antonio' instead of 'llamo'\"\n"
        "}\n"

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

def generate_general_feedback(messages: list[dict], only_user_messages: bool = False):
    """
    From conversation history, generate structured feedback with positives and improvements.
    Always returns both structured output (if possible) and raw model output.
    """
    if only_user_messages:
        messages = [m for m in messages if m["role"] == "user"]

    formatted_conversation = "\n".join(
        f"{msg['role']}: {msg['content']}" for msg in messages
    )

    prompt = (
        "You are a Spanish language tutor providing concise, constructive, and encouraging feedback.\n"

        "TASK:\n"
        "Analyze the student's Spanish in the conversation and provide structured feedback.\n\n"

        "RULES:\n"
        "- Focus on real usage (grammar, word choice, simple sentence structure)\n"
        "- Be specific, avoid generic praise\n"
        "- Keep each point to 1 sentence\n"
        "- Tone must be encouraging\n\n"

        "FORMAT:\n"
        "- positive: 2-3 strengths\n"
        "- improvements: A list of 2-3 specific, actionable suggestions for improvement based on the user's mistakes\n"
        "- When writing in the target language, wrap it in << >> e.g., <<hola>>\n\n"

        f"CONVERSATION TO ANALYZE:\n{formatted_conversation}\n\n"

        "EXAMPLE OUTPUT:\n"
        "{\n"
        "  \"positive\": [\n"
        "    \"Good use of basic phrases like <<hola>> and <<gracias>>\",\n"
        "    \"Used correct verb conjugation in <<yo fui>> when talking about past events\",\n"
        "    \"Correctly formed simple sentences like <<yo como pan>>\"\n"
        "  ],\n"
        "  \"improvements\": [\n"
        "    \"You wrote <<yo es estudiante>>, but <<ser>> must match the subject which is first person singular 'yo'. It should be <<yo soy estudiante>>\",\n"
        "    \"You wrote <<me gusta los perros>>, but the verb <<gustar>> agrees with what is liked, which is the plural <<los perros>>. It should be <<me gustan los perros>>\"\n"
        "  ]\n"
        "}\n\n"

        "IMPORTANT:\n"
        "Return ONLY valid JSON. No extra text."
    )

    response = ollama.chat(
        model=FEEDBACK_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_output = response.message.content.strip()

    feedback = None
    error = None

    # direct Pydantic parse
    try:
        feedback = GeneralFeedbackResponse.model_validate_json(raw_output)

    except Exception:
        # extract JSON block if model adds extra text
        try:
            match = re.search(r"\{.*\}", raw_output, re.DOTALL)
            if match:
                cleaned = match.group()
                feedback = GeneralFeedbackResponse.model_validate_json(cleaned)
        except Exception as e:
            error = str(e)

    
    return {
        "GeneralFeedbackResponse": feedback,
        "raw_output": raw_output,
        "error": error
    }