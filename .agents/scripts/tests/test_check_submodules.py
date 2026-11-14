import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "check_submodules.py"
spec = importlib.util.spec_from_file_location("submodule_checker", SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class SubmoduleTests(unittest.TestCase):
    def git(self, repo, *args):
        return subprocess.check_output(["git", "-C", str(repo), *args],
                                       text=True, stderr=subprocess.DEVNULL).strip()

    def init(self, path):
        path.mkdir()
        self.git(path, "init", "-b", "main")
        self.git(path, "config", "user.name", "Test")
        self.git(path, "config", "user.email", "test@example.invalid")

    def commit(self, repo, name="file.txt"):
        p = repo / name
        p.write_text(p.read_text() + "update\n" if p.exists() else "initial\n")
        self.git(repo, "add", "--", name)
        self.git(repo, "commit", "-m", "test update")
        return self.git(repo, "rev-parse", "HEAD")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "workspace"
        self.init(self.root)
        self.child = self.root / "module with space"
        self.init(self.child)
        self.sha = self.commit(self.child)
        self.child_remote = self.base / "child.git"
        self.parent_remote = self.base / "parent.git"
        for repo, remote in ((self.child, self.child_remote), (self.root, self.parent_remote)):
            subprocess.run(["git", "init", "--bare", str(remote)], check=True,
                           capture_output=True)
            self.git(repo, "remote", "add", "origin", str(remote))
        self.push(self.child)
        self.git(self.root, "config", "--file", ".gitmodules", "submodule.component.path", self.child.name)
        self.git(self.root, "config", "--file", ".gitmodules", "submodule.component.url", str(self.child_remote))
        self.git(self.root, "add", ".gitmodules")
        self.stage_pin(self.sha)
        self.git(self.root, "commit", "-m", "initial parent")
        self.push(self.root)

    def push(self, repo, branch="main"):
        self.git(repo, "push", "origin", "HEAD:refs/heads/" + branch)

    def stage_pin(self, sha):
        self.git(self.root, "update-index", "--add", "--cacheinfo", "160000", sha, self.child.name)

    def report(self, **kwargs):
        return checker.inspect(self.root, "main", live=True, **kwargs)

    def advance_child(self):
        sha = self.commit(self.child)
        self.push(self.child)
        return sha

    def test_all_layers_synced_and_read_only(self):
        status = self.git(self.root, "status", "--porcelain")
        index = (self.root / ".git/index").read_bytes()
        head = self.git(self.child, "rev-parse", "HEAD")
        result = self.report()
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["status"], "synced")
        self.assertEqual(self.git(self.root, "status", "--porcelain"), status)
        self.assertEqual((self.root / ".git/index").read_bytes(), index)
        self.assertEqual(self.git(self.child, "rev-parse", "HEAD"), head)

    def test_parent_stale_after_child_main_advances(self):
        new = self.advance_child()
        result = self.report()
        self.assertEqual(result["exit_code"], 1)
        row = result["submodules"][0]
        self.assertEqual(row["local_head"], new)
        self.assertEqual(row["parent_published_pin"], self.sha)
        self.assertIn("parent_published_pin_differs_from_target", row["issues"])

    def test_staged_gitlink_does_not_mean_committed_or_published(self):
        new = self.advance_child()
        self.stage_pin(new)
        row = self.report()["submodules"][0]
        self.assertEqual(row["parent_index_pin"], new)
        self.assertEqual(row["parent_head_pin"], self.sha)
        self.assertEqual(row["parent_published_pin"], self.sha)

    def test_local_parent_commit_does_not_mean_published(self):
        new = self.advance_child()
        self.stage_pin(new)
        self.git(self.root, "commit", "-m", "new gitlink")
        result = self.report()
        row = result["submodules"][0]
        self.assertEqual(row["parent_head_pin"], new)
        self.assertEqual(row["parent_published_pin"], self.sha)
        self.assertEqual(result["exit_code"], 1)

    def test_local_child_not_in_selected_target_is_reported(self):
        new = self.commit(self.child)
        row = self.report()["submodules"][0]
        self.assertEqual(row["target_head"], self.sha)
        self.assertEqual(row["local_head"], new)
        self.assertIn("local_head_differs_from_target", row["issues"])

    def test_dirty_child_is_not_full_sync(self):
        (self.child / "pending.txt").write_text("pending")
        result = self.report()
        self.assertEqual(result["exit_code"], 1)
        self.assertIn("child_has_uncommitted_changes", result["submodules"][0]["issues"])

    def test_missing_child_cannot_resolve_to_parent(self):
        shutil.rmtree(self.child)
        self.child.mkdir()
        result = self.report()
        self.assertEqual(result["exit_code"], 2)
        self.assertIsNone(result["submodules"][0]["local_head"])

    def test_offline_cache_never_claims_live_sync(self):
        shutil.rmtree(self.child_remote)
        result = checker.inspect(self.root, "main", live=False)
        self.assertEqual(result["exit_code"], 2)
        self.assertEqual(result["source"], "cached_unverified")

    def test_remote_failure_is_unknown_and_does_not_expose_url(self):
        shutil.rmtree(self.child_remote)
        result = self.report()
        self.assertEqual(result["exit_code"], 2)
        self.assertNotIn(str(self.child_remote), json.dumps(result))

    def test_remote_parent_commit_missing_locally_needs_fetch(self):
        other = self.base / "other"
        subprocess.run(["git", "clone", "--branch", "main", str(self.parent_remote), str(other)],
                       check=True, capture_output=True)
        self.git(other, "config", "user.name", "Test")
        self.git(other, "config", "user.email", "test@example.invalid")
        self.commit(other)
        self.push(other)
        result = self.report()
        self.assertEqual(result["exit_code"], 2)
        self.assertIsNone(result["submodules"][0]["parent_published_pin"])
        self.assertIn("fetch parent", result["errors"][0])

    def test_explicit_non_main_target(self):
        self.push(self.child, "release")
        self.push(self.root, "release")
        self.advance_child()
        result = checker.inspect(self.root, "release", live=True)
        self.assertEqual(result["target"], "release")
        self.assertEqual(result["submodules"][0]["target_head"], self.sha)
        self.assertEqual(result["exit_code"], 1)  # Checkout main advanced; release stayed pinned.

    def test_path_outside_workspace_rejected(self):
        self.git(self.root, "config", "--file", ".gitmodules", "submodule.component.path", "../outside")
        result = self.report()
        self.assertEqual(result["exit_code"], 2)
        self.assertIn("escapes", result["submodules"][0]["errors"][0])


if __name__ == "__main__":
    unittest.main()
