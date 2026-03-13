from typing import List, Dict, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):

    persona: str
    message: str
    history: Optional[List[Dict[str, str]]] = []  # [{role: 'user'/'bot', message: str}]
    custom_bio: Optional[str] = None


class Persona(BaseModel):

    id: int | None = None
    name: str
    era: str
    bio: str
