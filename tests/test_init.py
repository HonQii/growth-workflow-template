import json
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "init.py"


class InitializeTests(unittest.TestCase):
    def run_init(self, project):
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(project)],
            capture_output=True,
            text=True,
        )

    def test_copies_workspace_and_preserves_project(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "project with spaces"
            project.mkdir()
            rules = project / "AGENTS.md"
            rules.write_text("Existing project rules\n")
            result = self.run_init(project)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(rules.read_text(), "Existing project rules\n")
            self.assertTrue((project / "growth" / "SETUP.md").is_file())
            self.assertTrue((project / "growth" / "output" / "README.md").is_file())
            metadata = json.loads((project / "growth" / "template.json").read_text())
            self.assertEqual(metadata["name"], "growth-workflow-template")
            self.assertFalse((project / ".git").exists())
            self.assertFalse((project / "growth" / ".git").exists())

    def test_existing_workspace_is_unchanged_on_retry(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.assertEqual(self.run_init(project).returncode, 0)
            strategy = project / "growth" / "context" / "strategy.md"
            strategy.write_text("Real project decisions\n")
            before = {p.relative_to(project): p.read_bytes()
                      for p in project.rglob("*") if p.is_file()}
            result = self.run_init(project)
            self.assertNotEqual(result.returncode, 0)
            after = {p.relative_to(project): p.read_bytes()
                     for p in project.rglob("*") if p.is_file()}
            self.assertEqual(before, after)

    def test_local_credentials_and_evidence_are_not_copied(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            template = root / "template"
            (template / "scripts").mkdir(parents=True)
            shutil.copy2(SCRIPT, template / "scripts/init.py")
            source = template / "growth"
            source.mkdir()
            for name in ("config.local.json", ".env", "AuthKey.p8", "config.example.json", ".gitignore"):
                (source / name).write_text("fixture")
            for name in (".local-data", "__pycache__", ".venv"):
                (source / name).mkdir()
                (source / name / "private.txt").write_text("private")
            (source / "linked-secret").symlink_to(source / "AuthKey.p8")
            target = root / "target"
            target.mkdir()
            result = subprocess.run([sys.executable, str(template / "scripts/init.py"), str(target)], capture_output=True)
            self.assertEqual(result.returncode, 0)
            self.assertEqual({p.name for p in (target / "growth").iterdir()}, {"config.example.json", ".gitignore"})

    def test_missing_project_is_not_created(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "missing"
            self.assertNotEqual(self.run_init(project).returncode, 0)
            self.assertFalse(project.exists())

    def test_dangling_growth_symlink_is_not_followed(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            missing = project / "missing"
            link = project / "growth"
            link.symlink_to(missing, target_is_directory=True)
            self.assertNotEqual(self.run_init(project).returncode, 0)
            self.assertTrue(link.is_symlink())
            self.assertFalse(missing.exists())


if __name__ == "__main__":
    unittest.main()
