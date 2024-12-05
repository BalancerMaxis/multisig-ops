from pathlib import Path


def find_project_root(current_path=None):
    # Find the project root by looking for multisigs.md anchor file
    anchor_file = "multisigs.md"
    if current_path is None:
        current_path = Path(__file__).resolve().parent
    if (current_path / anchor_file).exists():
        return current_path
    parent = current_path.parent
    if parent == current_path:
        raise FileNotFoundError("Project root not found")
    return find_project_root(parent)
