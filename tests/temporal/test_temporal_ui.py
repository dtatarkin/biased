import pytest

from biased.temporal.dtos import TemporalClientParams, TemporalParams
from biased.temporal.services.temporal_ui import TemporalUi


def _ui(base_url: str, namespace: str = "default") -> TemporalUi:
    return TemporalUi(
        TemporalParams(ui_base_url=base_url),  # type: ignore[arg-type]
        TemporalClientParams(target_host="localhost:7233", namespace=namespace),
    )


@pytest.mark.parametrize(
    ("base_url", "expected"),
    [
        (
            "http://localhost:8233",
            "http://localhost:8233/namespaces/default/workflows/wf",
        ),
        (
            "http://localhost:8233/",
            "http://localhost:8233/namespaces/default/workflows/wf",
        ),
        (
            "https://ops.example.com/temporal/",
            "https://ops.example.com/temporal/namespaces/default/workflows/wf",
        ),
    ],
)
def test_keeps_the_base_path(base_url, expected):
    assert str(_ui(base_url).build_workflow_url("wf")) == expected


@pytest.mark.parametrize(
    ("workflow_id", "segment"),
    [
        ("echo-a/b?c#d", "echo-a%2Fb%3Fc%23d"),
        ("echo-%41", "echo-%2541"),
        ("echo hi", "echo%20hi"),
    ],
)
def test_encodes_the_workflow_id_as_one_segment(workflow_id, segment):
    url = _ui("http://localhost:8233").build_workflow_url(workflow_id)
    assert str(url) == f"http://localhost:8233/namespaces/default/workflows/{segment}"


def test_encodes_the_namespace():
    url = _ui("http://localhost:8233", namespace="a/b").build_workflow_url("wf")
    assert str(url) == "http://localhost:8233/namespaces/a%2Fb/workflows/wf"
