from typing import List
from fastapi import APIRouter, HTTPException
from backend.schema import Persona
from backend.db import get_db


router = APIRouter()


@router.get("/", response_model=List[Persona])
def get_personas() -> List[Persona]:
    """
    Retrieve a list of all personas from the database.

    Returns
    -------
    List[Persona]
        A list of Persona objects representing all personas in the database.
    """

    with get_db() as conn:
        cur = conn.execute("SELECT id, name, era, bio FROM personas")
        rows = cur.fetchall()
        return [Persona(id=row[0], name=row[1], era=row[2], bio=row[3]) for row in rows]


@router.get("/{persona_id}", response_model=Persona)
def get_persona(persona_id: int) -> Persona:
    """
    Retrieve a single persona by its ID.

    Parameters
    ----------
    persona_id : int
        The ID of the persona to retrieve.

    Returns
    -------
    Persona
        A Persona object representing the requested persona.
    """

    with get_db() as conn:
        cur = conn.execute("SELECT id, name, era, bio FROM personas WHERE id = ?", (persona_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Persona not found")
        return Persona(id=row[0], name=row[1], era=row[2], bio=row[3])


@router.post("/", response_model=Persona)
def create_persona(persona: Persona) -> Persona:
    """
    Create a new persona in the database.

    Parameters
    ----------
    persona : Persona
        The Persona object to create.

    Returns
    -------
    Persona
        The created Persona object with its assigned ID.
    """

    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO personas (name, era, bio) VALUES (?, ?, ?)",
            (persona.name, persona.era, persona.bio)
        )
        conn.commit()
        persona_id = cur.lastrowid
        return get_persona(persona_id)


@router.put("/{persona_id}", response_model=Persona)
def update_persona(persona_id: int, persona: Persona) -> Persona:
    """
    Update an existing persona in the database.

    Parameters
    ----------
    persona_id : int
        The ID of the persona to update.
    persona : Persona
        The Persona object containing the updated data.

    Returns
    -------
    Persona
        The updated Persona object.
    """

    with get_db() as conn:
        cur = conn.execute(
            "UPDATE personas SET name = ?, era = ?, bio = ? WHERE id = ?",
            (persona.name, persona.era, persona.bio, persona_id)
        )
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Persona not found")
        return get_persona(persona_id)


@router.delete("/{persona_id}")
def delete_persona(persona_id: int) -> dict:
    """
    Delete a persona from the database.

    Parameters
    ----------
    persona_id : int
        The ID of the persona to delete.

    Returns
    -------
    dict
        A dictionary containing a message indicating the deletion status.
    """

    with get_db() as conn:
        cur = conn.execute("DELETE FROM personas WHERE id = ?", (persona_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Persona not found")
    return {"detail": "Persona deleted"}
