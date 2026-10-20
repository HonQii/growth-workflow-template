"""Project-local credential loading without execution, leaks, or cwd dependence."""
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "growth/scripts"))
import data as cli
from growth_data.environment import load_environment
from growth_data.auth import apple_token
from growth_data.core import DataError


class EnvironmentTests(unittest.TestCase):
    def test_supported_literals_paths_and_process_precedence(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {"GROWTH_GOOGLE_ACCESS_TOKEN": "runner"}, clear=True):
            path = Path(temp)/".env"
            path.write_text('export GROWTH_GOOGLE_ACCESS_TOKEN=file\nGROWTH_APPLE_KEY_ID="key#id" # comment\nGROWTH_APPLE_ISSUER_ID=issuer # comment\nGROWTH_APPLE_PRIVATE_KEY_PATH="../keys/auth key.p8"\nGROWTH_APPLE_ACCESS_TOKEN=literal$VALUE\nUNRELATED_SETTING=ignored\n')
            load_environment(path)
            self.assertEqual(os.environ["GROWTH_GOOGLE_ACCESS_TOKEN"], "runner")
            self.assertEqual(os.environ["GROWTH_APPLE_KEY_ID"], "key#id")
            self.assertEqual(os.environ["GROWTH_APPLE_ISSUER_ID"], "issuer")
            self.assertEqual(Path(os.environ["GROWTH_APPLE_PRIVATE_KEY_PATH"]).resolve(), (Path(temp)/"../keys/auth key.p8").resolve())
            self.assertEqual(os.environ["GROWTH_APPLE_ACCESS_TOKEN"], "literal$VALUE")
            self.assertNotIn("UNRELATED_SETTING", os.environ)

    def test_blank_example_does_not_break_adc_discovery(self):
        with patch.dict(os.environ, {}, clear=True):
            load_environment(ROOT/"growth/.env.example")
            self.assertEqual(dict(os.environ), {})

    def test_bad_file_is_atomic_and_does_not_leak_values(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {}, clear=True):
            path = Path(temp)/".env"
            path.write_text('GROWTH_APPLE_KEY_ID=private-value\nGROWTH_APPLE_ACCESS_TOKEN="unclosed-private\n')
            with self.assertRaises(DataError) as caught:
                load_environment(path)
            self.assertNotIn("private", str(caught.exception))
            self.assertNotIn("GROWTH_APPLE_KEY_ID", os.environ)
            path.write_text('GROWTH_APPLE_KEY_ID=one\nGROWTH_APPLE_KEY_ID=two\n')
            with self.assertRaises(DataError):
                load_environment(path)

    def test_missing_default_allowed_explicit_missing_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/"missing"
            load_environment(path)
            with self.assertRaises(DataError) as caught:
                load_environment(path, required=True)
            self.assertEqual(caught.exception.code, "env_file_missing")

    def test_apple_ids_from_environment_with_json_fallback(self):
        jwt = Mock()
        jwt.encode.return_value = "signed-token"
        with tempfile.TemporaryDirectory() as temp:
            key = Path(temp)/"key.p8"
            key.write_text("synthetic-key")
            env = {"GROWTH_APPLE_PRIVATE_KEY_PATH": str(key), "GROWTH_APPLE_KEY_ID": "env-key", "GROWTH_APPLE_ISSUER_ID": "env-issuer"}
            with patch.dict(os.environ, env, clear=True), patch.dict(sys.modules, {"jwt": jwt}):
                self.assertEqual(apple_token({"key_id": "json-key", "issuer_id": "json-issuer"})(), "signed-token")
                self.assertEqual(jwt.encode.call_args.args[0]["iss"], "env-issuer")
                self.assertEqual(jwt.encode.call_args.kwargs["headers"]["kid"], "env-key")
                os.environ["GROWTH_APPLE_KEY_ID"] = ""
                os.environ["GROWTH_APPLE_ISSUER_ID"] = ""
                apple_token({"key_id": "json-key", "issuer_id": "json-issuer"})()
                self.assertEqual(jwt.encode.call_args.kwargs["headers"]["kid"], "json-key")

    def test_cli_loads_its_workspace_file_not_cwd(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {}, clear=True):
            root = Path(temp)
            (root/".env").write_text("GROWTH_APPLE_KEY_ID=workspace\n")
            (root/"config.local.json").write_text(json.dumps({"project": "test", "sources": {"gsc": {"enabled": True}}}))
            def inspect(*args):
                self.assertEqual(os.environ["GROWTH_APPLE_KEY_ID"], "workspace")
                return {"status": "ok"}
            with patch.object(cli, "GROWTH", root), patch.object(cli, "run_source", side_effect=inspect), patch("sys.stdout", new_callable=io.StringIO):
                self.assertEqual(cli.main(["doctor", "all"]), 0)

    def test_explicit_file_and_copy_exclusions(self):
        with tempfile.TemporaryDirectory() as temp:
            subprocess.run([sys.executable, str(ROOT/"scripts/init.py"), temp], check=True, capture_output=True)
            growth = Path(temp)/"growth"
            self.assertTrue((growth/".env.example").is_file())
            self.assertFalse((growth/".env").exists())
            external = Path(temp)/"runner.env"
            external.write_text('GROWTH_GOOGLE_ACCESS_TOKEN="private-unclosed\n')
            run = subprocess.run([sys.executable, str(growth/"scripts/data.py"), "--env-file", str(external), "doctor", "all"], capture_output=True, text=True, cwd="/private/tmp")
            self.assertEqual(run.returncode, 1)
            self.assertEqual(json.loads(run.stdout)["error_code"], "invalid_env")
            self.assertNotIn("private-unclosed", run.stdout+run.stderr)


if __name__ == "__main__":
    unittest.main()
