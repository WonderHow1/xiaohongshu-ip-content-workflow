#!/usr/bin/env python3
"""Check dependencies; install missing allowlisted skills via the host installer."""

import argparse
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys


SKILL_DIR = Path(__file__).resolve().parents[1]
MANIFEST = SKILL_DIR / "references" / "dependencies.json"


def unique_paths(paths):
    result = []
    for path in paths:
        path = Path(path).expanduser().resolve()
        if path not in result:
            result.append(path)
    return result


def default_destination():
    return Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "skills"


def skill_identity(path):
    file = path if path.name == "SKILL.md" else path / "SKILL.md"
    try:
        text = file.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None, None
    if not text.startswith("---"):
        return None, None
    parts = text.split("---", 2)
    if len(parts) != 3:
        return None, None
    name = re.search(r"(?m)^name:\s*['\"]?([a-zA-Z0-9_-]+)['\"]?\s*$", parts[1])
    version = re.search(r"(?m)^\s*version:\s*['\"]?([0-9][0-9A-Za-z_.+-]*)", parts[1])
    return (name.group(1) if name else None, version.group(1) if version else None)


def locate_skill(name, roots, explicit):
    candidates = []
    if name in explicit:
        candidates.append(explicit[name])
    for root in roots:
        candidates.extend((root / name, root / ".system" / name))
    invalid = []
    for path in unique_paths(candidates):
        if not path.exists():
            continue
        identity, version = skill_identity(path)
        if identity == name:
            return {"name": name, "status": "present", "path": str(path), "version": version}
        invalid.append(str(path))
    if invalid:
        return {"name": name, "status": "invalid", "paths": invalid,
                "next_action": "preserve_existing_and_review"}
    return {"name": name, "status": "missing"}


def find_installer(roots, explicit):
    if explicit:
        candidate = Path(explicit).expanduser().resolve()
        return candidate if candidate.is_file() else None
    for root in roots:
        for base in (root / ".system", root):
            candidate = base / "skill-installer" / "scripts" / "install-skill-from-github.py"
            if candidate.is_file():
                return candidate
    return None


def run_installer(command, timeout):
    process = None
    try:
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            start_new_session=(os.name == "posix"),
        )
        # Output is deliberately not echoed; helpers can print environment details.
        process.communicate(timeout=timeout)
        return "finished", process.returncode
    except subprocess.TimeoutExpired:
        if process is not None:
            if os.name == "posix":
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            else:
                try:
                    # Windows helpers can spawn git; terminate that process tree too.
                    subprocess.run(
                        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        timeout=5, check=False,
                    )
                except (OSError, subprocess.TimeoutExpired):
                    process.kill()
                if process.poll() is None:
                    process.kill()
            try:
                process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                for stream in (process.stdout, process.stderr):
                    if stream:
                        stream.close()
        return "timeout", None
    except OSError:
        return "could_not_start", None


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true", help="Read-only; this is the default.")
    modes.add_argument("--install", action="store_true",
                       help="Install missing GitHub skills; caller must have user and host authorization.")
    parser.add_argument("--dest", type=Path, default=default_destination())
    parser.add_argument("--skill-root", action="append", type=Path, default=[])
    parser.add_argument("--only-specified-roots", action="store_true",
                       help="Inspect only --dest, --skill-root and --skill-path locations.")
    parser.add_argument("--skill-path", action="append", default=[], metavar="NAME=PATH")
    parser.add_argument("--installer-script", type=Path)
    parser.add_argument("--only-skill", action="append", default=[],
                       help="Install only this declared GitHub skill; repeat to select several.")
    parser.add_argument("--method", choices=("auto", "download", "git"), default="auto")
    parser.add_argument("--timeout", type=float, default=90)
    parser.add_argument("--tools-checked", action="store_true",
                       help="Agent has inspected the current visible tool inventory.")
    parser.add_argument("--available-tool", action="append", default=[])
    args = parser.parse_args(argv)
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    explicit = {}
    for item in args.skill_path:
        name, separator, value = item.partition("=")
        if not separator or not name or not value:
            parser.error("--skill-path must be NAME=PATH")
        explicit[name] = Path(value)
    if args.available_tool and not args.tools_checked:
        parser.error("--available-tool requires --tools-checked")
    return args, explicit


def main(argv=None):
    args, explicit = parse_args(argv)
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        entries = manifest["skills"]
        if manifest["schema_version"] != 1:
            raise ValueError("unsupported manifest")
    except (OSError, ValueError, KeyError):
        print(json.dumps({"status": "invalid_dependency_manifest"}))
        return 2
    names = {entry["name"] for entry in entries}
    if set(explicit) - names:
        print(json.dumps({"status": "unknown_skill_path_name"}))
        return 2
    installable = {entry["name"] for entry in entries if entry["install_kind"] == "github"}
    selected = set(args.only_skill) if args.only_skill else installable
    if selected - installable:
        print(json.dumps({"status": "only_declared_github_skills_are_installable"}))
        return 2
    destination = args.dest.expanduser().resolve()
    locations = [*args.skill_root, destination]
    if not args.only_specified_roots:
        locations.extend([
            default_destination(), Path.home() / ".agents" / "skills",
            Path.cwd() / ".agents" / "skills",
        ])
    roots = unique_paths(locations)
    installer = find_installer(roots, args.installer_script)
    results = []
    installed_count = 0
    for entry in entries:
        name = entry["name"]
        state = locate_skill(name, roots, explicit)
        state["install_kind"] = entry["install_kind"]
        if state["status"] == "missing" and entry["install_kind"] == "github":
            state["source"] = {
                field: entry[field] for field in ("repo", "path", "ref", "source_url")
            }
            if name not in selected:
                state["next_action"] = "not_requested_for_install"
            elif not args.install:
                state["next_action"] = "install_with_authorization"
            elif installer is None:
                state["next_action"] = "needs_client_installer"
            elif (destination / name).exists():
                # A concurrent or previously malformed install must not be overwritten.
                state["status"] = "invalid"
                state["next_action"] = "preserve_existing_and_review"
            else:
                command = [
                    sys.executable, str(installer), "--repo", entry["repo"],
                    "--path", entry["path"], "--ref", entry["ref"],
                    "--dest", str(destination), "--method", args.method,
                ]
                outcome, returncode = run_installer(command, args.timeout)
                state["attempt"] = {"outcome": outcome, "returncode": returncode}
                checked = locate_skill(name, roots, explicit)
                if outcome == "finished" and returncode == 0 and checked["status"] == "present":
                    state.update(checked)
                    state["installed_this_run"] = True
                    installed_count += 1
                else:
                    state["status"] = checked["status"] if checked["status"] == "invalid" else "failed"
                    state["next_action"] = "inspect_client_permissions_network_or_installer"
        elif state["status"] == "missing":
            state["next_action"] = "requires_client_builtin_skill"
        results.append(state)

    tools = args.available_tool
    social = (any(name == "research_social_signals" or
                  name.endswith("__research_social_signals") for name in tools)
              if args.tools_checked else None)
    image = (any(name in {"imagegen", "image_gen.imagegen"} or
                 (name.startswith("image_gen") and name.endswith("__imagegen"))
                 for name in tools) if args.tools_checked else None)
    present = {item["name"]: item["status"] == "present" for item in results}
    preflight_complete = (all(present.values()) and social is True and image is True)
    report = {
        "schema_version": 1,
        "mode": "install" if args.install else "check",
        "installed_count": installed_count,
        "requested_install_skills": sorted(selected) if args.install else [],
        "requested_install_complete": (
            all(item["status"] == "present" for item in results if item["name"] in selected)
            if args.install else None
        ),
        "skills": results,
        "tools": {"inventory_checked": args.tools_checked,
                  "social_research_visible": social, "native_imagegen_visible": image},
        "preflight_complete": preflight_complete,
        "authentication": "not_verified_by_this_script",
        "plugins_or_connections_installed_by_this_script": False,
        "next_steps": [],
    }
    if not args.tools_checked:
        report["next_steps"].append("inspect_current_tool_inventory")
    elif social is False:
        report["next_steps"].append("discover_or_connect_signaldig_through_client")
    if image is False or not present.get("imagegen"):
        report["next_steps"].append("verify_client_builtin_imagegen")
    if any(item.get("installed_this_run") for item in results):
        report["next_steps"].append("reload_skill_instructions_and_recheck_visible_tools")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.install and any(
        item["name"] in selected and item["status"] != "present" for item in results
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
