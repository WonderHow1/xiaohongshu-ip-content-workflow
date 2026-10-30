#!/usr/bin/env python3
"""Read-only release checks. Standard library only; no network or paid tools."""

from pathlib import Path
import re
import struct
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "xiaohongshu-ip-content-studio"
REQUIRED = (
    ROOT / "README.md",
    ROOT / "LICENSE",
    ROOT / "LICENSE_SCOPE.md",
    ROOT / ".gitignore",
    SKILL / "SKILL.md",
    SKILL / "agents" / "openai.yaml",
    SKILL / "references" / "accounts" / "template.md",
    SKILL / "references" / "setup.md",
    SKILL / "references" / "content-formats.md",
    SKILL / "references" / "dependencies.json",
    SKILL / "scripts" / "setup_dependencies.py",
    SKILL / "assets" / "huangxiaoxie" / "NOTICE.md",
)
PRIVATE_NAMES = {
    "accounts.json", "history.json", "run.json", "research.json", "review.md",
    ".xiaohongshu-ip-content-studio.json", ".xiaohongshu-ip-studio.json", "setup-status.json",
}
PRIVATE_TOP_DIRS = {"outputs", "work", "state", ".local", ".codex", ".agents"}
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".json", ".txt"}
LEAK_PATTERNS = (
    ("machine-specific home path", re.compile(r"/(?:Users|home)/[A-Za-z0-9_.-]+/")),
    ("Windows user path", re.compile(
        r"\b[A-Za-z]:[\\/](?:Users|Documents and Settings)[\\/][A-Za-z0-9_. -]+[\\/]")),
    ("local temporary path", re.compile(r"/private/(?:tmp|var/folders)/")),
    ("research token", re.compile(r"\b(?:sg2|rr1)\.[A-Za-z0-9_=.-]{30,}")),
    ("OpenAI-style secret", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}")),
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}")),
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
)


def within_root(path):
    try:
        path.relative_to(ROOT)
        return True
    except ValueError:
        return False


def validate():
    errors = []
    files = []
    png_sizes = []
    for path in REQUIRED:
        if not path.is_file():
            errors.append(f"Missing required file: {path.relative_to(ROOT)}")

    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if any(part in {".git", "__pycache__"} for part in relative.parts):
            continue
        if path.is_symlink():
            errors.append(f"Symlinks are not included in this release: {relative}")
            continue
        if not path.is_file():
            continue
        files.append(path)
        if path.name in {".DS_Store", "Thumbs.db"}:
            errors.append(f"OS directory metadata shipped: {relative}")
        if relative.parts[0] in PRIVATE_TOP_DIRS:
            errors.append(f"Local-only directory shipped: {relative}")
        if path.name in PRIVATE_NAMES or path.name == ".env" or path.name.startswith(".env."):
            errors.append(f"Runtime/credential file shipped: {relative}")
        if path.suffix.lower() in {".pem", ".key", ".zip"}:
            errors.append(f"Unexpected credential/archive file shipped: {relative}")

        if path.suffix.lower() == ".png":
            with path.open("rb") as stream:
                header = stream.read(24)
            if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
                errors.append(f"Invalid PNG header: {relative}")
            else:
                width, height = struct.unpack(">II", header[16:24])
                if not width or not height:
                    errors.append(f"Invalid PNG dimensions: {relative}")
                png_sizes.append((str(relative), width, height))
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {
            "LICENSE", ".gitignore"
        }:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"Text file is not UTF-8: {relative}")
            continue
        for label, pattern in LEAK_PATTERNS:
            if pattern.search(text):
                # Do not print matched values, which might be credentials.
                errors.append(f"Possible {label} in {relative}")

        if path.suffix.lower() == ".md":
            targets = re.findall(r"\[[^\]]*\]\(([^)\s]+)\)", text)
            targets += re.findall(r'<img\b[^>]*\bsrc=["\']([^"\']+)["\']', text)
            for target in targets:
                if target.startswith(("#", "https://", "http://", "mailto:")):
                    continue
                target = target.split("#", 1)[0]
                destination = (path.parent / target).resolve()
                if not within_root(destination):
                    errors.append(f"Link escapes release directory: {relative}")
                elif not destination.exists():
                    errors.append(f"Broken local link in {relative}: {target}")

    for name in ("LICENSE", "LICENSE_SCOPE.md"):
        root_license, installed_license = ROOT / name, SKILL / name
        if not installed_license.is_file():
            errors.append(f"Installable skill missing {name}")
        elif root_license.is_file() and root_license.read_bytes() != installed_license.read_bytes():
            errors.append(f"Root and installable skill disagree on {name}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Release checks passed: {len(files)} files.")
    print("No detected private paths, runtime records or common credential patterns.")
    print("Local links and packaged license files verified.")
    for name, width, height in png_sizes:
        print(f"PNG {width}x{height}: {name}")
    print("No network, research, generation or publishing was performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(validate())
