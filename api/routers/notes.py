import os
from typing import List, Literal, Optional

from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from api.models import NoteCreate, NoteGenerateRequest, NoteResponse, NoteUpdate
from open_notebook.domain.notebook import Note, Notebook, Source
from open_notebook.domain.transformation import Transformation
from open_notebook.exceptions import (
    InvalidInputError,
    NotFoundError,
    OpenNotebookError,
)

router = APIRouter()


@router.get("/notes", response_model=List[NoteResponse])
async def get_notes(
    notebook_id: Optional[str] = Query(None, description="Filter by notebook ID"),
):
    """Get all notes with optional notebook filtering."""
    try:
        if notebook_id:
            # Get notes for a specific notebook
            from open_notebook.domain.notebook import Notebook

            notebook = await Notebook.get(notebook_id)
            notes = await notebook.get_notes()
        else:
            # Get all notes
            notes = await Note.get_all(order_by="updated desc")

        return [
            NoteResponse(
                id=note.id or "",
                title=note.title,
                content=note.content,
                note_type=note.note_type,
                created=str(note.created),
                updated=str(note.updated),
            )
            for note in notes
        ]
    except HTTPException:
        raise
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Notebook not found")
    except OpenNotebookError:
        raise
    except Exception as e:
        logger.error(f"Error fetching notes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching notes: {str(e)}")


@router.post("/notes", response_model=NoteResponse)
async def create_note(note_data: NoteCreate):
    """Create a new note."""
    try:
        # Auto-generate title if not provided and it's an AI note
        title = note_data.title
        if not title and note_data.note_type == "ai" and note_data.content:
            from open_notebook.graphs.prompt import graph as prompt_graph

            prompt = "Based on the Note below, please provide a Title for this content, with max 15 words"
            # LangGraph accepts a partial state dict at runtime, but its typed
            # overloads require the full state type (langgraph typing limitation).
            result = await prompt_graph.ainvoke(  # type: ignore[call-overload]
                {
                    "input_text": note_data.content,
                    "prompt": prompt,
                }
            )
            title = result.get("output", "Untitled Note")

        # Validate note_type
        note_type: Optional[Literal["human", "ai"]] = None
        if note_data.note_type in ("human", "ai"):
            note_type = note_data.note_type  # type: ignore[assignment]
        elif note_data.note_type is not None:
            raise HTTPException(
                status_code=400, detail="note_type must be 'human' or 'ai'"
            )

        new_note = Note(
            title=title,
            content=note_data.content,
            note_type=note_type,
        )
        command_id = await new_note.save()

        # Add to notebook if specified
        if note_data.notebook_id:
            from open_notebook.domain.notebook import Notebook

            # Verify the notebook exists (raises NotFoundError -> 404)
            await Notebook.get(note_data.notebook_id)
            await new_note.add_to_notebook(note_data.notebook_id)

        return NoteResponse(
            id=new_note.id or "",
            title=new_note.title,
            content=new_note.content,
            note_type=new_note.note_type,
            created=str(new_note.created),
            updated=str(new_note.updated),
            command_id=str(command_id) if command_id else None,
        )
    except HTTPException:
        raise
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Notebook not found")
    except InvalidInputError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except OpenNotebookError:
        raise
    except Exception as e:
        logger.error(f"Error creating note: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating note: {str(e)}")


NOTE_GENERATION_MAX_CHARS_ENV = "OPEN_NOTEBOOK_NOTE_GENERATION_MAX_CHARS"
DEFAULT_NOTE_GENERATION_MAX_CHARS = 600_000
NOTE_TITLE_PROMPT = (
    "Write a short title (at most 12 words) for the note below, in the same "
    "language as the note. Reply with the title only, without quotes."
)


def _note_generation_max_chars() -> int:
    raw = os.environ.get(NOTE_GENERATION_MAX_CHARS_ENV, "").strip()
    try:
        value = int(raw) if raw else DEFAULT_NOTE_GENERATION_MAX_CHARS
    except ValueError:
        return DEFAULT_NOTE_GENERATION_MAX_CHARS
    return value if value > 0 else DEFAULT_NOTE_GENERATION_MAX_CHARS


async def _sources_text(notebook: Notebook, source_ids: Optional[List[str]]) -> str:
    """Full text of the chosen notebook sources, one section per source."""
    sources: List[Source] = await notebook.get_sources(include_full_text=True)
    if source_ids:
        by_id = {str(src.id): src for src in sources}
        if any(sid not in by_id for sid in source_ids):
            raise InvalidInputError(
                "Some of the selected sources are not in this notebook"
            )
        sources = [by_id[sid] for sid in dict.fromkeys(source_ids)]
    usable = [src for src in sources if src.full_text and src.full_text.strip()]
    if not usable:
        raise InvalidInputError("The selected sources have no text yet")
    text = "\n\n---\n\n".join(
        f"# {src.title or 'Untitled source'}\n\n{(src.full_text or '').strip()}"
        for src in usable
    )
    limit = _note_generation_max_chars()
    if len(text) > limit:
        raise InvalidInputError(
            f"The selected sources are too long together ({len(text)} characters, "
            f"limit {limit}). Select fewer sources."
        )
    return text


async def _generate_title(content: str, fallback: str) -> str:
    from open_notebook.graphs.prompt import graph as prompt_graph

    try:
        # LangGraph accepts a partial state dict at runtime (typing limitation).
        result = await prompt_graph.ainvoke(  # type: ignore[call-overload]
            {"input_text": content[:20_000], "prompt": NOTE_TITLE_PROMPT}
        )
        title = str(result.get("output") or "").strip().strip("\"'#*").strip()
    except Exception as e:
        logger.warning(f"Note title generation failed: {type(e).__name__}")
        title = ""
    title = " ".join(title.split())
    return (title[:200] if title else fallback)[:200]


@router.post("/notes/generate", response_model=NoteResponse)
async def generate_note(request: NoteGenerateRequest):
    """Generate an AI note from notebook sources (transformation or free prompt).

    Runs synchronously like POST /transformations/execute: the note exists
    when the call returns.
    """
    try:
        notebook = await Notebook.get(request.notebook_id)
        input_text = await _sources_text(notebook, request.source_ids)

        if request.transformation_id:
            transformation = await Transformation.get(request.transformation_id)
            fallback_title = transformation.title or transformation.name
        else:
            prompt = (request.prompt or "").strip()
            # Not saved: only carries the user's instruction through the same
            # graph (default instructions, length checks, thinking cleanup).
            transformation = Transformation(
                name="note-from-prompt",
                title=prompt[:80],
                description="",
                prompt=prompt,
                apply_default=False,
            )
            fallback_title = prompt[:120]

        from open_notebook.graphs.transformation import graph as transformation_graph

        model_id = request.model_id or transformation.model_id
        # LangGraph accepts a partial state dict at runtime (typing limitation).
        result = await transformation_graph.ainvoke(  # type: ignore[call-overload]
            dict(input_text=input_text, transformation=transformation),
            config=dict(configurable={"model_id": model_id}),
        )
        content = str(result["output"])

        title = (request.title or "").strip() or await _generate_title(
            content, fallback_title
        )
        note = Note(title=title, content=content, note_type="ai")
        command_id = await note.save()
        await note.add_to_notebook(request.notebook_id)

        return NoteResponse(
            id=note.id or "",
            title=note.title,
            content=note.content,
            note_type=note.note_type,
            created=str(note.created),
            updated=str(note.updated),
            command_id=str(command_id) if command_id else None,
        )
    except OpenNotebookError:
        raise  # typed errors -> 400 / 404 / 422 / 502 via global handlers
    except Exception as e:
        logger.error(f"Error generating note: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating note")


@router.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(note_id: str):
    """Get a specific note by ID."""
    try:
        note = await Note.get(note_id)

        return NoteResponse(
            id=note.id or "",
            title=note.title,
            content=note.content,
            note_type=note.note_type,
            created=str(note.created),
            updated=str(note.updated),
        )
    except HTTPException:
        raise
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Note not found")
    except OpenNotebookError:
        raise
    except Exception as e:
        logger.error(f"Error fetching note {note_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching note: {str(e)}")


@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str, note_update: NoteUpdate):
    """Update a note."""
    try:
        note = await Note.get(note_id)

        # Update only provided fields
        if note_update.title is not None:
            note.title = note_update.title
        if note_update.content is not None:
            note.content = note_update.content
        if note_update.note_type is not None:
            if note_update.note_type in ("human", "ai"):
                note.note_type = note_update.note_type  # type: ignore[assignment]
            else:
                raise HTTPException(
                    status_code=400, detail="note_type must be 'human' or 'ai'"
                )

        command_id = await note.save()

        return NoteResponse(
            id=note.id or "",
            title=note.title,
            content=note.content,
            note_type=note.note_type,
            created=str(note.created),
            updated=str(note.updated),
            command_id=str(command_id) if command_id else None,
        )
    except HTTPException:
        raise
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Note not found")
    except InvalidInputError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except OpenNotebookError:
        raise
    except Exception as e:
        logger.error(f"Error updating note {note_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating note: {str(e)}")


@router.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    """Delete a note."""
    try:
        note = await Note.get(note_id)

        await note.delete()

        return {"message": "Note deleted successfully"}
    except HTTPException:
        raise
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Note not found")
    except OpenNotebookError:
        raise
    except Exception as e:
        logger.error(f"Error deleting note {note_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting note: {str(e)}")
