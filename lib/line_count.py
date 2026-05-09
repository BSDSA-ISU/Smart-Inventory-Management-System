from pathlib import Path

TEXT_EXTENSIONS = {
    ".py", ".html", ".css", ".js",
    ".json", ".sql", ".md", ".txt"
}

IGNORE_DIRS = {
    ".git", "__pycache__", "node_modules",
    ".venv", "venv", "dist", "build"
}

_cached = None

def get_loc():
    global _cached
    if _cached is None:
        _cached = count()
    return _cached

def count(path="."):
    total = 0

    for file in Path(path).rglob("*"):
        if not file.is_file():
            continue

        if any(part in IGNORE_DIRS for part in file.parts):
            continue

        if file.suffix.lower() not in TEXT_EXTENSIONS:
            continue

        try:
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                total += sum(1 for _ in f)
        except:
            pass

    return total