import importlib.util
import io
import json
import os
from pathlib import Path
import ssl
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).parents[1] / "skills/mro-inquiry-match/scripts/check_skill_update.py"
SPEC = importlib.util.spec_from_file_location("skill_updates", SCRIPT)
updates = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(updates)


def skill_text(version):
    return f'---\nname: mro-inquiry-match\nmetadata:\n  version: "{version}"\n---\nLocal instructions\n'


class DailySkillUpdateTests(unittest.TestCase):
    def test_numeric_version_and_daily_cache_keep_pending_update_until_installed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "SKILL.md"
            skill.write_text(skill_text("1.9.0"))
            with patch.object(updates, "fetch_skill", return_value=skill_text("1.10.0")) as fetch:
                first = updates.check_update(root, root / "cache", "2026-11-12")
                self.assertEqual(first["status"], "update_available")
                self.assertFalse(first["cached"])
                self.assertEqual(skill.read_text(), skill_text("1.9.0"))
                again = updates.check_update(root, root / "cache", "2026-11-12")
                self.assertEqual(again["status"], "update_available")
                self.assertTrue(again["cached"])
                self.assertEqual(fetch.call_count, 1)
                skill.write_text(skill_text("1.10.0"))
                installed = updates.check_update(root, root / "cache", "2026-11-12")
                self.assertEqual(installed["status"], "up_to_date")
                self.assertTrue(installed["cached"])
                updates.check_update(root, root / "cache", "2026-11-13")
                self.assertEqual(fetch.call_count, 2)

    def test_failed_check_preserves_last_success_and_allows_later_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SKILL.md").write_text(skill_text("1.4.0"))
            with patch.object(updates, "fetch_skill", return_value=skill_text("1.4.0")):
                updates.check_update(root, root / "cache", "2026-11-11")
            state = next((root / "cache").glob("*.json"))
            previous = state.read_bytes()
            for failure in [TimeoutError(), ValueError("malformed version")]:
                with patch.object(updates, "fetch_skill", side_effect=failure):
                    result = updates.check_update(root, root / "cache", "2026-11-12")
                self.assertEqual(result["status"], "check_failed")
                self.assertEqual(state.read_bytes(), previous)
            with patch.object(updates, "fetch_skill", return_value=skill_text("1.4.1")):
                result = updates.check_update(root, root / "cache", "2026-11-12")
            self.assertEqual(result["status"], "update_available")
            self.assertEqual(json.loads(state.read_text())["checkedDate"], "2026-11-12")

    def test_never_downgrades_and_force_bypasses_today_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SKILL.md").write_text(skill_text("1.4.0"))
            with patch.object(updates, "fetch_skill", return_value=skill_text("1.3.1")):
                result = updates.check_update(root, root / "cache", "2026-11-12")
            self.assertEqual(result["status"], "up_to_date")
            with patch.object(updates, "fetch_skill", return_value=skill_text("1.4.1")) as fetch:
                result = updates.check_update(root, root / "cache", "2026-11-12", force=True)
                self.assertEqual(fetch.call_count, 1)
            self.assertEqual(result["status"], "update_available")

    def test_github_request_has_no_mro_credentials_and_verifies_tls(self):
        with patch.dict(os.environ, {"MRO_API_KEY": "private-key"}):
            with patch.object(updates, "urlopen", return_value=io.BytesIO(skill_text("1.4.0").encode())) as request:
                self.assertEqual(updates.read_version(updates.fetch_skill()), (1, 4, 0))
        self.assertIsNone(request.call_args.args[0].get_header("Authorization"))
        self.assertEqual(request.call_args.kwargs["context"].verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(request.call_args.kwargs["context"].check_hostname)


if __name__ == "__main__":
    unittest.main()
