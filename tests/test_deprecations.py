import re
from pathlib import Path

# Fast, import-free checks for deprecated API usages or risky patterns.
# This test reads files as text only — it does NOT import the project.

ROOT = Path(__file__).resolve().parent.parent

# patterns -> (regex, message)
DEPRECATED_PATTERNS = {
    "torchvision_pretrained": (
        re.compile(r"\bpretrained\s*=\s*True\b"),
        "Use the `weights=` enum (e.g. `weights=ResNet18_Weights.DEFAULT`) instead of `pretrained=True`.",
    ),
    "streamlit_use_column_width": (
        re.compile(r"use_column_width\s*=\s*True"),
        "`use_column_width` is deprecated — use `use_container_width`.",
    ),
    "register_backward_hook": (
        re.compile(r"register_backward_hook\s*\("),
        "Prefer `register_full_backward_hook` (or provide a safe fallback) to avoid missing grad_input in future PyTorch versions.",
    ),
    "file_uploader_type_case_sensitive": (
        re.compile(r"file_uploader\([^\)]*type\s*=\s*\["),
        "Avoid using `type=` with case-sensitive extensions; validate at runtime instead to prevent deserialization errors.",
    ),
}

INCLUDE_EXTS = {".py", ".ipynb", ".md"}


def search_files():
    matches = {}
    for p in ROOT.rglob("*"):
        if p.is_file() and p.suffix in INCLUDE_EXTS and ".git" not in p.parts:
            text = p.read_text(encoding="utf-8", errors="ignore")
            for name, (regex, msg) in DEPRECATED_PATTERNS.items():
                for m in regex.finditer(text):
                    loc = (p.relative_to(ROOT), text.count("\n", 0, m.start()) + 1)
                    matches.setdefault(name, []).append((loc, m.group(0), msg))
    return matches


def test_no_deprecated_patterns():
    matches = search_files()
    if matches:
        lines = [
            "Deprecated/unsafe patterns detected — please address before merging:\n"
        ]
        for name, hits in matches.items():
            lines.append(f"Pattern: {name}")
            for (path, lineno), snippet, msg in hits:
                lines.append(f"  - {path}:{lineno}: `{snippet.strip()}` -> {msg}")
            lines.append("")
        full = "\n".join(lines)
        raise AssertionError(full)
    # otherwise pass silently
