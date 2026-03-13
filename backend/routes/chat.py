import requests
from typing import Dict, List

from fastapi import APIRouter, HTTPException

from backend.schema import ChatRequest, Persona
from backend.db import get_db
from backend.config import OPENAI_API_KEY, HUGGINGFACE_API_TOKEN, \
    HUGGINGFACE_MODEL, LLM_PROVIDER


router = APIRouter()


def generate_prompt(
        persona: Persona,
        user_message: str,
        history: List[Dict[str, str]]
     ) -> str:
    """
    Generate a prompt for the LLM based on the selected persona, user message,
    and conversation history.

    Parameters
    ----------
    persona : Persona
        The selected persona for the conversation.
    user_message : str
        The latest message from the user.
    history : List[Dict[str, str]]
        The conversation history, where each turn is a dictionary with 'role'
        and 'message' keys.

    Returns
    -------
    str
        The generated prompt to be sent to the LLM.
    """
    
    prompt = f"""You are {persona.name}, a historical figure from {persona.era}. Respond to the user as {persona.name} would, using their knowledge, tone, and style. Stay in character and avoid modern references. Keep your responses concise and under 3 sentences.\nBackground: {persona.bio}\n"""
    for turn in history:
        prompt += f"\n{turn['role'].capitalize()}: {turn['message']}"
    prompt += f"\nUser: {user_message}\n{persona.name}: "
    return prompt


@router.post("/")
def chat(request: ChatRequest) -> dict:
    """
    Handle a chat request by generating a response from the LLM based on the
    selected persona and conversation history.

    Parameters
    ----------
    request : ChatRequest
        The chat request containing the persona, message, and history.

    Returns
    -------
    dict
        A dictionary containing the LLM's response and the generated prompt.

    Raises
    ------
    HTTPException
        If the persona is not found, if the custom bio is missing for a custom
        persona, or if the persona ID is invalid.
    """

    if request.persona == "custom":
        if not request.custom_bio:
            raise HTTPException(
                status_code=400,
                detail="Custom bio is required for custom persona"
            )
        persona = Persona(
            name="Custom Persona",
            era="N/A",
            bio=request.custom_bio
        )
    else:
        # request.persona is expected to be the persona_id (int or str convertible to int)
        try:
            persona_id = int(request.persona)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid persona id")
        with get_db() as conn:
            cur = conn.execute("SELECT id, name, era, bio FROM personas WHERE id = ?", (persona_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Persona not found")
            persona = Persona(id=row[0], name=row[1], era=row[2], bio=row[3])
    prompt = generate_prompt(persona, request.message, request.history or [])
    response_text = ""
    if LLM_PROVIDER == "openai" and OPENAI_API_KEY:
        try:
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": prompt}
                    ]
                },
                timeout=15
            )
            resp.raise_for_status()
            data = resp.json()
            response_text = data["choices"][0]["message"]["content"]
        except Exception as e:
            response_text = f"[LLM error: {str(e)}]"
    elif LLM_PROVIDER == "huggingface" and HUGGINGFACE_API_TOKEN:
        try:
            hf_url = "https://router.huggingface.co/v1/chat/completions"
            resp = requests.post(
                hf_url,
                headers={
                    "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "model": HUGGINGFACE_MODEL,
                    "stream": False
                },
                timeout=30
            )
            resp.raise_for_status()
            data = resp.json()
            # HuggingFace router returns OpenAI-compatible response
            response_text = data["choices"][0]["message"]["content"]
        except Exception as e:
            response_text = f"[LLM error: {str(e)}]"
    else:
        response_text = f"[LLM integration not configured. Prompt: {prompt[:100]}...]"
    return {"response": response_text, "prompt": prompt}
