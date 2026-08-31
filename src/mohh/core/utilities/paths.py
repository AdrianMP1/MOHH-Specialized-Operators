
from pathlib import Path

def project_root() -> str:
    """
    Repo root, resolved from this file's location so grammars/ and
    datasets/ are found regardless of the invocation directory.
    """
    return str(Path(__file__).resolve().parents[4])
