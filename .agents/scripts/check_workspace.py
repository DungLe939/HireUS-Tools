#!/usr/bin/env python3
"""Check shared HireUS skills, guidance, JSON/TOML and ignore rules offline."""

import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

try:
    import tomllib
except ImportError:
    tomllib = None


ROOT = Path(__file__).resolve().parents[2]
REPOS = (".", "frontend", "backend", "documents")
LOCAL_SPEC_FILES = {"feature.json", "integrations/packages.json"}


def is_local_state(path):
    parts = path.parts
    if "__pycache__" in parts or ".sync_incoming" in parts:
        return True
    if path.name in {".sync_manifest.json", ".DS_Store"} or path.suffix in {".pyc", ".pyo"}:
        return True
    if ".specify" in parts:
        relative = Path(*parts[parts.index(".specify") + 1:])
        if relative.as_posix() in LOCAL_SPEC_FILES:
            return True
        if relative.parts[:2] == ("integrations", "packages"):
            return True
        if (len(relative.parts) == 3 and relative.parts[0] == "extensions"
                and relative.parts[-1] == "local-config.yml"):
            return True
    return False


def shared_files(repo):
    files = {repo / name for name in
             ("AGENTS.md", "PROJECT_SOURCES.md", "README.md", ".codex/config.toml")
             if (repo / name).is_file()}
    for directory in (".agents", ".codex/agents", ".specify"):
        files.update(p for p in (repo / directory).rglob("*")
                     if p.is_file() and not is_local_state(p.relative_to(repo)))
    return sorted(files)


def skill_shape_errors(path, content):
    """Check catalog fields only; this is not a complete YAML parser."""
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", content, re.S)
    if not match:
        return ["missing SKILL.md frontmatter"]
    header = match.group(1)
    name_match = re.search(r"(?m)^name:[ \t]*(.+?)\s*$", header)
    desc_match = re.search(r"(?m)^description:[ \t]*(.+?)\s*$", header)
    errors = []
    if not name_match:
        errors.append("missing skill name")
    else:
        name = name_match.group(1).strip().strip("\"'")
        if (name != path.parent.name or len(name) > 64
                or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name)):
            errors.append("skill name must match its directory and use lowercase hyphens")
    if not desc_match or desc_match.group(1).strip() in {"", "''", '""'}:
        errors.append("missing skill description")
    return errors


def main():
    errors = []
    warnings = []
    available = []
    for name in REPOS:
        repo = ROOT / name
        if not repo.is_dir() or not (repo / ".git").exists():
            errors.append(f"{name}: missing Git checkout; initialize submodules if needed")
            continue
        available.append((name, repo))
        if not (repo / "AGENTS.md").is_file():
            errors.append(f"{name}: missing AGENTS.md")
    checker = ROOT / "documents/.agents/scripts/check_docs.py"
    if not checker.is_file():
        for error in errors:
            print("ERROR: " + error)
        print("ERROR: missing documents checker; initialize the documents submodule")
        return 1
    spec = importlib.util.spec_from_file_location("hireus_docs_checker", checker)
    docs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(docs)

    shared_count = 0
    untracked_count = 0
    checked = {"guides": 0, "skills": 0, "json": 0, "toml": 0}
    for name, repo in available:
        files = shared_files(repo)
        shared_count += len(files)
        relative = [p.relative_to(repo).as_posix() for p in files]
        if relative:
            ignored = subprocess.run(
                ["git", "check-ignore", "--no-index", "--stdin", "-z"], cwd=repo,
                input="\0".join(relative) + "\0", text=True, capture_output=True)
            if ignored.returncode not in (0, 1):
                errors.append(f"{name}: cannot inspect ignore rules: {ignored.stderr.strip()}")
            else:
                errors.extend(f"{name}: shared file is ignored: {p}"
                              for p in ignored.stdout.split("\0") if p)
        tracked = subprocess.run(["git", "ls-files", "-z"], cwd=repo,
                                 capture_output=True, text=True)
        if tracked.returncode:
            errors.append(f"{name}: cannot inspect Git index: {tracked.stderr.strip()}")
        else:
            index = set(tracked.stdout.split("\0"))
            untracked_count += sum(p not in index for p in relative)

        for path in files:
            if path.suffix not in {".md", ".json", ".toml"}:
                continue
            source = path.relative_to(ROOT).as_posix()
            try:
                content = path.read_text(encoding="utf-8-sig")
                if path.suffix == ".md":
                    checked["guides"] += 1
                    for target in docs.links(content, ".md"):
                        problem = docs.check_link(source, target, lambda p: (ROOT / p).exists())
                        if problem:
                            errors.append(f"{source}: {problem}: {target}")
                    if path.name == "SKILL.md":
                        checked["skills"] += 1
                        errors.extend(f"{source}: {problem}"
                                      for problem in skill_shape_errors(path, content))
                elif path.suffix == ".json":
                    checked["json"] += 1
                    json.loads(content)
                elif tomllib is None:
                    warnings.append(f"{source}: TOML not checked; Python 3.11+ required")
                else:
                    checked["toml"] += 1
                    data = tomllib.loads(content)
                    if path.parent.name == "agents" and path.parent.parent.name == ".codex":
                        for field in ("name", "description", "developer_instructions"):
                            if not isinstance(data.get(field), str) or not data[field].strip():
                                errors.append(f"{source}: missing reviewer field {field}")
            except (OSError, UnicodeError, ValueError) as exc:
                errors.append(f"{source}: cannot validate file: {exc}")

    for error in errors:
        print("ERROR: " + error)
    for warning in warnings:
        print("WARN: " + warning)
    print(f"Checked {checked['guides']} guides, {checked['skills']} skill catalogs, "
          f"{checked['json']} JSON and {checked['toml']} TOML files; "
          f"{shared_count} shared files: {len(errors)} errors, {len(warnings)} warnings.")
    if untracked_count:
        print(f"INFO: {untracked_count} new shared files are not in the Git index yet; "
              "include them when committing the requested changes.")
    for command in ("python3", "git", "pwsh", "specify"):
        print(f"TOOL: {command}: {shutil.which(command) or 'not found in PATH'}")
    if not shutil.which("pwsh"):
        print("INFO: PowerShell helpers are unavailable; skills may still be followed "
              "directly with file tools as documented.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
