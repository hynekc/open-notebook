"""Tests for POST /api/notes/generate (AI notes from notebook sources)."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from open_notebook.exceptions import NotFoundError


@pytest.fixture
def client():
    from api.main import app

    return TestClient(app)


def _source(sid, title, text):
    return SimpleNamespace(id=sid, title=title, full_text=text)


SOURCES = [
    _source("source:a", "Rybníky", "Rybník je umělá vodní nádrž."),
    _source("source:b", "Třeboňsko", "Třeboňsko má stovky rybníků."),
    _source("source:c", "Prázdný", ""),
]


@pytest.fixture
def mocks():
    notebook = MagicMock()
    notebook.get_sources = AsyncMock(return_value=SOURCES)
    note = MagicMock()
    note.id = "note:new"
    note.created = "2026-11-24T00:00:00Z"
    note.updated = "2026-11-24T00:00:00Z"
    note.save = AsyncMock(return_value="command:embed1")
    note.add_to_notebook = AsyncMock()
    graph = MagicMock()
    graph.ainvoke = AsyncMock(return_value={"output": "Shrnutí o rybnících."})
    title_graph = MagicMock()
    title_graph.ainvoke = AsyncMock(return_value={"output": '"Rybníky v Čechách"'})

    def make_note(**kwargs):
        note.title = kwargs["title"]
        note.content = kwargs["content"]
        note.note_type = kwargs["note_type"]
        return note

    with (
        patch(
            "api.routers.notes.Notebook.get", AsyncMock(return_value=notebook)
        ) as nb_get,
        patch("api.routers.notes.Note", side_effect=make_note),
        patch("open_notebook.graphs.transformation.graph", graph),
        patch("open_notebook.graphs.prompt.graph", title_graph),
    ):
        yield SimpleNamespace(
            notebook=notebook,
            note=note,
            graph=graph,
            title_graph=title_graph,
            nb_get=nb_get,
        )


def test_prompt_mode_uses_all_sources_with_text_and_generates_title(client, mocks):
    response = client.post(
        "/api/notes/generate",
        json={"notebook_id": "notebook:1", "prompt": "Shrň rybníky"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["content"] == "Shrnutí o rybnících."
    assert body["title"] == "Rybníky v Čechách"
    assert body["note_type"] == "ai"
    assert body["command_id"] == "command:embed1"

    state = mocks.graph.ainvoke.call_args.args[0]
    assert state["transformation"].prompt == "Shrň rybníky"
    assert "# Rybníky" in state["input_text"] and "# Třeboňsko" in state["input_text"]
    assert "Prázdný" not in state["input_text"]
    mocks.note.add_to_notebook.assert_awaited_once_with("notebook:1")


def test_transformation_mode_with_selected_sources_and_title(client, mocks):
    transformation = SimpleNamespace(
        title="Husté shrnutí", name="dense", model_id="model:x"
    )
    with patch(
        "api.routers.notes.Transformation.get", AsyncMock(return_value=transformation)
    ):
        response = client.post(
            "/api/notes/generate",
            json={
                "notebook_id": "notebook:1",
                "transformation_id": "transformation:1",
                "source_ids": ["source:b"],
                "title": "Moje poznámka",
            },
        )
    assert response.status_code == 200, response.text
    assert response.json()["title"] == "Moje poznámka"
    mocks.title_graph.ainvoke.assert_not_called()
    state = mocks.graph.ainvoke.call_args.args[0]
    assert "Třeboňsko" in state["input_text"] and "Rybník je" not in state["input_text"]
    config = mocks.graph.ainvoke.call_args.kwargs["config"]
    assert config["configurable"]["model_id"] == "model:x"


def test_title_falls_back_when_title_generation_fails(client, mocks):
    mocks.title_graph.ainvoke.side_effect = RuntimeError("model down")
    response = client.post(
        "/api/notes/generate",
        json={"notebook_id": "notebook:1", "prompt": "Co je rybník?"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Co je rybník?"


@pytest.mark.parametrize(
    "payload",
    [
        {"notebook_id": "notebook:1"},
        {"notebook_id": "notebook:1", "prompt": "   "},
        {
            "notebook_id": "notebook:1",
            "prompt": "x",
            "transformation_id": "transformation:1",
        },
    ],
)
def test_exactly_one_instruction_required(client, mocks, payload):
    assert client.post("/api/notes/generate", json=payload).status_code == 422


def test_source_from_other_notebook_rejected(client, mocks):
    response = client.post(
        "/api/notes/generate",
        json={"notebook_id": "notebook:1", "prompt": "x", "source_ids": ["source:zzz"]},
    )
    assert response.status_code == 400
    mocks.graph.ainvoke.assert_not_called()


def test_sources_without_text_rejected(client, mocks):
    response = client.post(
        "/api/notes/generate",
        json={"notebook_id": "notebook:1", "prompt": "x", "source_ids": ["source:c"]},
    )
    assert response.status_code == 400


def test_too_long_sources_rejected(client, mocks, monkeypatch):
    monkeypatch.setenv("OPEN_NOTEBOOK_NOTE_GENERATION_MAX_CHARS", "20")
    response = client.post(
        "/api/notes/generate", json={"notebook_id": "notebook:1", "prompt": "x"}
    )
    assert response.status_code == 400
    assert "too long" in response.json()["detail"]


def test_missing_notebook_is_404(client, mocks):
    mocks.nb_get.side_effect = NotFoundError("Notebook not found")
    response = client.post(
        "/api/notes/generate", json={"notebook_id": "notebook:none", "prompt": "x"}
    )
    assert response.status_code == 404
