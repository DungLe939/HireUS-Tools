#!/usr/bin/env python3
"""Read-only comparison of submodule checkouts, parent gitlinks and target branches."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess


class CheckError(Exception):
    pass


def git(repo, *args, optional=False):
    try:
        result = subprocess.run(["git", "--no-optional-locks", "-C", str(repo), *args],
                                capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        raise CheckError("Git unavailable or timed out") from None
    if result.returncode:
        if optional:
            return None
        # Git stderr can include private remote URLs. Do not expose it.
        raise CheckError("Git operation failed: " + args[0])
    return result.stdout.strip()


def target_ref(repo, remote, branch, live):
    if remote not in (git(repo, "remote") or "").splitlines():
        raise CheckError("Configured remote is missing")
    if live:
        output = git(repo, "ls-remote", "--refs", remote, "refs/heads/" + branch)
        lines = [l.split() for l in output.splitlines() if l]
        if len(lines) != 1 or lines[0][1] != "refs/heads/" + branch:
            raise CheckError("Target branch is missing on remote")
        return lines[0][0]
    sha = git(repo, "rev-parse", "--verify",
              "refs/remotes/" + remote + "/" + branch + "^{commit}", optional=True)
    if not sha:
        raise CheckError("Cached target is missing; fetch explicitly or use --remote")
    return sha


def pin(repo, ref, path):
    output = git(repo, "ls-tree", "-z", ref, "--", path)
    for entry in output.split("\0"):
        if not entry:
            continue
        metadata, name = entry.split("\t", 1)
        mode, kind, sha = metadata.split()
        if name == path and mode == "160000" and kind == "commit":
            return sha
    return None


def index_pin(repo, path):
    output = git(repo, "ls-files", "--stage", "-z", "--", path)
    for entry in output.split("\0"):
        if not entry:
            continue
        metadata, name = entry.split("\t", 1)
        mode, sha, stage = metadata.split()
        if name == path and mode == "160000" and stage == "0":
            return sha
    return None


def inspect(root, target, remote="origin", live=False, parent_target=None):
    root = Path(root).resolve()
    actual_root = Path(git(root, "rev-parse", "--show-toplevel")).resolve()
    if root != actual_root:
        raise CheckError("--root must be the parent repository root")
    parent_target = parent_target or target
    for branch in (target, parent_target):
        git(root, "check-ref-format", "refs/heads/" + branch)
    definitions = git(root, "config", "--file", ".gitmodules", "--get-regexp",
                      r"^submodule\..*\.path$", optional=True)
    if not definitions:
        raise CheckError("No submodule paths found in .gitmodules")
    paths = [line.split(None, 1)[1] for line in definitions.splitlines()]
    if len(set(paths)) != len(paths):
        raise CheckError("Duplicate submodule paths")
    report = {"checked_at": datetime.now(timezone.utc).isoformat(),
              "source": "live_remote" if live else "cached_unverified",
              "target": target, "parent_target": parent_target,
              "parent_head": git(root, "rev-parse", "HEAD"),
              "parent_remote_head": None, "errors": [], "submodules": []}
    parent_commit = None
    try:
        report["parent_remote_head"] = target_ref(root, remote, parent_target, live)
        if git(root, "cat-file", "-e", report["parent_remote_head"] + "^{commit}", optional=True) is None:
            raise CheckError("Parent target commit not available locally; fetch parent and rerun")
        parent_commit = report["parent_remote_head"]
    except CheckError as error:
        report["errors"].append(str(error))
    for path in paths:
        row = {"path": path, "local_head": None, "target_head": None,
               "parent_head_pin": None, "parent_index_pin": None,
               "parent_published_pin": None, "dirty": None,
               "issues": [], "errors": []}
        report["submodules"].append(row)
        try:
            child = (root / path).resolve()
            if child == root or root not in child.parents:
                raise CheckError("Submodule path escapes the parent repository")
            row["parent_head_pin"] = pin(root, "HEAD", path)
            row["parent_index_pin"] = index_pin(root, path)
            if parent_commit:
                row["parent_published_pin"] = pin(root, parent_commit, path)
            # An uninitialized directory must not silently resolve to the parent Git repository.
            top = git(child, "rev-parse", "--show-toplevel", optional=True)
            if not top or Path(top).resolve() != child:
                raise CheckError("Submodule checkout is missing or uninitialized")
            row["local_head"] = git(child, "rev-parse", "HEAD")
            row["dirty"] = bool(git(child, "status", "--porcelain", "--untracked-files=normal"))
            row["target_head"] = target_ref(child, remote, target, live)
            for field in ("local_head", "parent_head_pin", "parent_index_pin"):
                if row[field] != row["target_head"]:
                    row["issues"].append(field + "_differs_from_target")
            if parent_commit and row["parent_published_pin"] != row["target_head"]:
                row["issues"].append("parent_published_pin_differs_from_target")
            if row["dirty"]:
                row["issues"].append("child_has_uncommitted_changes")
        except CheckError as error:
            row["errors"].append(str(error))
    unknown = (not live or bool(report["errors"])
               or any(row["errors"] for row in report["submodules"]))
    drift = any(row["issues"] for row in report["submodules"])
    report["status"] = "unverified" if unknown else "needs_sync" if drift else "synced"
    report["exit_code"] = 2 if unknown else 1 if drift else 0
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--target", required=True, help="Explicit child target branch, e.g. main")
    parser.add_argument("--parent-target", help="Parent branch to verify; defaults to --target")
    parser.add_argument("--remote-name", default="origin")
    parser.add_argument("--remote", action="store_true", help="Query live refs; does not fetch or modify Git")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = inspect(args.root, args.target, args.remote_name, args.remote, args.parent_target)
    except CheckError as error:
        report = {"status": "unverified", "exit_code": 2, "errors": [str(error)], "submodules": []}
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("Source:", report.get("source", "unknown"), "| Status:", report["status"])
        print("repo | local | target | parent HEAD | parent index | parent published")
        for row in report["submodules"]:
            fields = [row["path"]] + [(row[k] or "?")[:10] for k in
                      ("local_head", "target_head", "parent_head_pin", "parent_index_pin", "parent_published_pin")]
            print(" | ".join(fields))
            for message in row["issues"] + row["errors"]:
                print("  " + message)
        for message in report["errors"]:
            print("ERROR:", message)
        if report.get("source") == "cached_unverified":
            print("Cached refs only: use --remote for live verification; no claim of latest state.")
    return report["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
