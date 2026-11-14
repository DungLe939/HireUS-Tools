import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "sync_main.py"
spec = importlib.util.spec_from_file_location("sync_main", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SyncMainTests(unittest.TestCase):
    def git(self, repo, *args):
        return subprocess.check_output(["git", "-C", str(repo), *args],
                                       text=True, stderr=subprocess.DEVNULL).strip()

    def commit(self, repo, name, content):
        (repo / name).write_text(content)
        self.git(repo, "add", "--", name)
        self.git(repo, "commit", "-m", "fixture")
        return self.git(repo, "rev-parse", "HEAD")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.remote = base / "remote.git"
        self.source = base / "source"
        self.repo = base / "member"
        subprocess.run(["git", "init", "--bare", str(self.remote)], check=True, capture_output=True)
        self.source.mkdir()
        self.git(self.source, "init", "-b", "main")
        self.git(self.source, "config", "user.name", "Test")
        self.git(self.source, "config", "user.email", "test@example.invalid")
        self.before = self.commit(self.source, "base.txt", "base")
        self.git(self.source, "remote", "add", "origin", str(self.remote))
        self.git(self.source, "push", "origin", "main")
        subprocess.run(["git", "clone", "--branch", "main", str(self.remote), str(self.repo)], check=True, capture_output=True)
        self.git(self.repo, "config", "user.name", "Test")
        self.git(self.repo, "config", "user.email", "test@example.invalid")
        self.git(self.repo, "switch", "-c", "member/epic")

    def advance(self, name="incoming.txt", content="incoming"):
        sha = self.commit(self.source, name, content)
        self.git(self.source, "push", "origin", "main")
        return sha

    def test_fast_forward_preserves_branch_and_does_not_push(self):
        sha = self.advance()
        result = module.sync(self.repo)
        self.assertEqual(result["status"], "fast_forwarded")
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), sha)
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), "member/epic")
        self.assertEqual(self.git(self.remote, "rev-parse", "main"), sha)
        self.assertFalse(self.git(self.remote, "for-each-ref", "refs/heads/member/epic"))

    def test_dirty_index_worktree_and_untracked_are_preserved(self):
        sha = self.advance()
        (self.repo / "base.txt").write_text("staged")
        self.git(self.repo, "add", "base.txt")
        (self.repo / "base.txt").write_text("unstaged")
        (self.repo / "mine.txt").write_text("mine")
        before = self.git(self.repo, "diff", "--cached")
        result = module.sync(self.repo)
        self.assertEqual(result["status"], "needs_attention")
        self.assertEqual(result["target_sha"], sha)
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), self.before)
        self.assertEqual(self.git(self.repo, "diff", "--cached"), before)
        self.assertEqual((self.repo / "base.txt").read_text(), "unstaged")
        self.assertEqual((self.repo / "mine.txt").read_text(), "mine")

    def test_diverged_clean_branch_creates_only_integration_merge(self):
        local = self.commit(self.repo, "feature.txt", "feature")
        remote = self.advance()
        result = module.sync(self.repo)
        self.assertEqual(result["status"], "merged")
        parents = self.git(self.repo, "show", "-s", "--format=%P", "HEAD").split()
        self.assertEqual(parents, [local, remote])
        self.assertEqual(self.git(self.remote, "rev-parse", "main"), remote)

    def test_conflict_aborts_without_leaving_merge_state(self):
        local = self.commit(self.repo, "base.txt", "local")
        self.advance("base.txt", "remote")
        result = module.sync(self.repo)
        self.assertEqual(result["status"], "needs_attention")
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), local)
        self.assertEqual((self.repo / "base.txt").read_text(), "local")
        self.assertFalse((self.repo / ".git/MERGE_HEAD").exists())
        self.assertFalse(self.git(self.repo, "status", "--porcelain"))

    def test_ignored_secret_is_not_overwritten_by_incoming_tracked_file(self):
        (self.repo / ".git/info/exclude").write_text(".env\n")
        (self.repo / ".env").write_text("private-local")
        self.advance(".env", "remote-content")
        result = module.sync(self.repo)
        self.assertEqual(result["status"], "needs_attention")
        self.assertEqual((self.repo / ".env").read_text(), "private-local")
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), self.before)

    def test_fetch_failure_does_not_claim_freshness(self):
        self.git(self.repo, "remote", "set-url", "origin", str(self.remote / "absent"))
        result = module.sync(self.repo)
        self.assertEqual(result["status"], "needs_attention")
        self.assertIsNone(result["target_sha"])
        self.assertNotIn(str(self.remote), result["message"])

    def test_detached_checkout_is_not_changed(self):
        self.git(self.repo, "checkout", "--detach")
        self.advance()
        self.assertEqual(module.sync(self.repo)["status"], "needs_attention")
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), self.before)

    def test_main_already_contained_allows_unfinished_feature_work(self):
        self.commit(self.repo, "feature.txt", "feature")
        (self.repo / "pending.txt").write_text("pending")
        result = module.sync(self.repo)
        self.assertEqual(result["status"], "up_to_date")
        self.assertEqual((self.repo / "pending.txt").read_text(), "pending")

    def test_existing_conflicted_merge_is_not_aborted(self):
        self.commit(self.repo, "base.txt", "local")
        self.advance("base.txt", "remote")
        self.git(self.repo, "fetch", "origin")
        attempted = subprocess.run(["git", "-C", str(self.repo), "merge", "--no-edit", "origin/main"],
                                   capture_output=True, text=True)
        self.assertNotEqual(attempted.returncode, 0)
        merge_head = (self.repo / ".git/MERGE_HEAD").read_bytes()
        content = (self.repo / "base.txt").read_bytes()
        result = module.sync(self.repo)
        self.assertEqual(result["status"], "needs_attention")
        self.assertEqual((self.repo / ".git/MERGE_HEAD").read_bytes(), merge_head)
        self.assertEqual((self.repo / "base.txt").read_bytes(), content)

    def test_non_checkout_directory_does_not_sync_its_parent(self):
        empty = self.repo / "uninitialized-module"
        empty.mkdir()
        self.advance()
        result = module.sync(empty)
        self.assertEqual(result["status"], "needs_attention")
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), self.before)


if __name__ == "__main__":
    unittest.main()
