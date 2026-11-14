#!/usr/bin/env python3
"""Fetch and integrate main on the current branch; preserve unfinished local work."""
import argparse
import json
from pathlib import Path
import subprocess


def git(repo, *args):
    return subprocess.run(["git", "--no-optional-locks", "-C", str(repo), *args],
                          capture_output=True, text=True, timeout=45)


def required(repo, *args):
    result = git(repo, *args)
    if result.returncode:
        raise RuntimeError("Git operation failed: " + args[0])
    return result.stdout.strip()


def sync(repo, remote="origin", target="main"):
    repo = Path(repo).resolve()
    out = {"repo": str(repo), "target": target, "branch": None,
           "before": None, "after": None, "target_sha": None,
           "status": "needs_attention", "message": "", "changed_files": []}
    try:
        if Path(required(repo, "rev-parse", "--show-toplevel")).resolve() != repo:
            raise RuntimeError("Select the exact repository root, not a missing submodule")
        required(repo, "check-ref-format", "refs/heads/" + target)
        if remote not in required(repo, "remote").splitlines():
            raise RuntimeError("Remote is not configured")
        out["before"] = out["after"] = required(repo, "rev-parse", "HEAD")
        branch = git(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
        if branch.returncode:
            raise RuntimeError("Detached HEAD; choose the intended member branch first")
        out["branch"] = branch.stdout.strip()
        for name in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply"):
            path = Path(required(repo, "rev-parse", "--git-path", name))
            if not path.is_absolute():
                path = repo / path
            if path.exists():
                raise RuntimeError("An existing Git operation is in progress; left untouched")
        # Force-update only this remote-tracking ref, never a local or published branch.
        result = git(repo, "fetch", "--no-recurse-submodules", remote,
                     "+refs/heads/" + target + ":refs/remotes/" + remote + "/" + target)
        if result.returncode:
            raise RuntimeError("Fetch failed; latest target could not be verified")
        sha = required(repo, "rev-parse", "--verify", "refs/remotes/" + remote + "/" + target + "^{commit}")
        out["target_sha"] = sha
        if git(repo, "merge-base", "--is-ancestor", sha, "HEAD").returncode == 0:
            out.update(status="up_to_date", message="Current branch already contains the fetched target")
            return out
        if required(repo, "status", "--porcelain", "--untracked-files=normal"):
            raise RuntimeError("Fetched target; integration skipped to preserve staged/unstaged/untracked work")
        ff = git(repo, "merge-base", "--is-ancestor", "HEAD", sha).returncode == 0
        args = ["-c", "submodule.recurse=false", "merge", "--no-edit", "--no-autostash", "--no-overwrite-ignore"]
        if ff:
            args.append("--ff-only")
        result = git(repo, *args, sha)
        out["after"] = required(repo, "rev-parse", "HEAD")
        if result.returncode:
            # Only abort the merge started above, which was entered with a clean tree.
            if git(repo, "rev-parse", "--verify", "MERGE_HEAD").returncode == 0:
                abort = git(repo, "merge", "--abort")
                if abort.returncode:
                    raise RuntimeError("Merge needs manual attention; abort failed, do not reset")
            out["after"] = required(repo, "rev-parse", "HEAD")
            raise RuntimeError("Integration blocked by conflict, hook, identity or protected local file; inspect before continuing")
        out["status"] = "fast_forwarded" if ff else "merged"
        out["message"] = "Target integrated; run checks for the incoming changes before coding"
        out["changed_files"] = required(repo, "diff", "--name-only", out["before"], out["after"]).splitlines()
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as error:
        # Do not print Git stderr or subprocess arguments: they may expose private remote URLs.
        out["status"] = "needs_attention"
        out["message"] = str(error) if isinstance(error, RuntimeError) else "Git unavailable or timed out; inspect repository state"
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", action="append", type=Path, help="Repo root; repeat for related repos")
    parser.add_argument("--remote-name", default="origin")
    parser.add_argument("--target", default="main")
    args = parser.parse_args()
    reports = [sync(path, args.remote_name, args.target) for path in (args.repo or [Path.cwd()])]
    print(json.dumps(reports, ensure_ascii=False, indent=2))
    return 2 if any(r["status"] == "needs_attention" for r in reports) else 0


if __name__ == "__main__":
    raise SystemExit(main())
