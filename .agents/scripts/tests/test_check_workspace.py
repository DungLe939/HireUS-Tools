import contextlib
import importlib.util
import io
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "check_workspace.py"
WORKSPACE = SCRIPT.parents[2]
spec = importlib.util.spec_from_file_location("workspace_checker", SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class WorkspaceChecks(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in checker.REPOS:
            repo = self.root / name
            repo.mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "init", "--quiet", str(repo)], check=True)
            (repo / "AGENTS.md").write_text("# Shared guidance\n", encoding="utf-8")
        target = self.root / "documents/.agents/scripts/check_docs.py"
        target.parent.mkdir(parents=True)
        shutil.copyfile(WORKSPACE / "documents/.agents/scripts/check_docs.py", target)

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def run_check(self):
        output = io.StringIO()
        with patch.object(checker, "ROOT", self.root), contextlib.redirect_stdout(output):
            result = checker.main()
        return result, output.getvalue()

    def test_valid_workspace_passes(self):
        self.assertEqual(self.run_check()[0], 0)

    def test_vendored_guidance_links_are_checked(self):
        self.write("frontend/.agents/skills/vercel-react-best-practices/AGENTS.md",
                   "[rule](rules/missing.md)\n")
        result, output = self.run_check()
        self.assertEqual(result, 1)
        self.assertIn("rules/missing.md", output)

    def test_spec_kit_template_links_are_checked(self):
        self.write("backend/.specify/templates/spec-template.md", "[source](missing.md)\n")
        result, output = self.run_check()
        self.assertEqual(result, 1)
        self.assertIn("spec-template.md", output)

    def test_ignored_tracked_skill_is_rejected(self):
        path = "frontend/.agents/skills/demo/SKILL.md"
        self.write(path, "---\nname: demo\ndescription: Shared demo workflow.\n---\n")
        subprocess.run(["git", "add", ".agents/skills/demo/SKILL.md"],
                       cwd=self.root / "frontend", check=True)
        self.write("frontend/.gitignore", ".agents/\n")
        result, output = self.run_check()
        self.assertEqual(result, 1)
        self.assertIn("shared file is ignored", output)

    def test_machine_local_cache_may_remain_ignored(self):
        self.write("backend/.specify/feature.json", "not shared or parsed")
        self.write("backend/.specify/.gitignore", "feature.json\n")
        self.write("documents/.agents/scripts/.sync_manifest.json", "local cache")
        self.write("documents/.gitignore", ".sync_manifest.json\n")
        self.assertEqual(self.run_check()[0], 0)

    def test_invalid_spec_kit_json_is_rejected(self):
        self.write("frontend/.specify/init-options.json", '{"integration":')
        result, output = self.run_check()
        self.assertEqual(result, 1)
        self.assertIn("init-options.json", output)

    @unittest.skipIf(checker.tomllib is None, "Python 3.11+ needed for TOML validation")
    def test_invalid_reviewer_toml_is_rejected(self):
        self.write("backend/.codex/agents/reviewer.toml", 'name = "unfinished')
        result, output = self.run_check()
        self.assertEqual(result, 1)
        self.assertIn("reviewer.toml", output)

    def test_skill_name_must_match_directory(self):
        self.write("frontend/.agents/skills/demo/SKILL.md",
                   "---\nname: another-name\ndescription: Shared workflow.\n---\n")
        result, output = self.run_check()
        self.assertEqual(result, 1)
        self.assertIn("skill name must match", output)

    def test_missing_submodule_is_reported_without_exception(self):
        shutil.rmtree(self.root / "frontend")
        result, output = self.run_check()
        self.assertEqual(result, 1)
        self.assertIn("frontend: missing Git checkout", output)


if __name__ == "__main__":
    unittest.main()
