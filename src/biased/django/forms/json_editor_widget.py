# An optional integration no extra declares, so the import does not resolve here.
from jsoneditor.forms import JSONEditor  # ty: ignore[unresolved-import]

default_json_editor_widget = JSONEditor(
    init_options={"mode": "code", "modes": ["view", "code", "tree"]},
)
