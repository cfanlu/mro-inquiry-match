import argparse
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

CLIENT = Path(__file__).parents[1] / "skills/mro-inquiry-match/scripts/mro_api_client.py"
SPEC = importlib.util.spec_from_file_location("mro_api_client", CLIENT)
client = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = client
SPEC.loader.exec_module(client)


class AccessClientTests(unittest.TestCase):
    def test_email_start_needs_no_key_and_never_sends_saved_credentials(self):
        for saved_key in ["", "private-key"]:
            response = io.BytesIO(b'{"success":true,"data":{"next":"check_email"}}')
            with patch.dict(os.environ, {"MRO_API_KEY": saved_key, "MRO_API_BASE_URL": client.DEFAULT_BASE_URL}, clear=True):
                with patch.object(client, "urlopen", return_value=response) as request:
                    result = client.call_api("POST", "/api/access/email/start", {"email": "buyer@example.com"}, 5)
            self.assertTrue(result["success"])
            self.assertIsNone(request.call_args.args[0].get_header("Authorization"))
            self.assertEqual(json.loads(request.call_args.args[0].data), {"email": "buyer@example.com"})
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(client.ApiError):
                client.call_api("POST", "/v1/match-inquiry", {}, 5)

    def test_structured_errors_keep_codes_and_only_same_site_actions(self):
        for url, expected in [(client.DEFAULT_BASE_URL + "/wallet", True), ("https://evil.example/wallet", False)]:
            body = json.dumps({"error": {"code": "insufficient_user_quota", "message": "recharge", "action": {"type": "recharge", "url": url}}}).encode()
            failure = HTTPError(client.DEFAULT_BASE_URL, 403, "Forbidden", {}, io.BytesIO(body))
            with patch.dict(os.environ, {"MRO_API_KEY": "private-key", "MRO_API_BASE_URL": client.DEFAULT_BASE_URL}, clear=True):
                with patch.object(client, "urlopen", side_effect=failure):
                    with self.assertRaises(client.ApiError) as caught:
                        client.call_api("POST", "/v1/match-inquiry", {}, 5)
            self.assertEqual(caught.exception.code, "insufficient_user_quota")
            self.assertEqual(bool(caught.exception.action), expected)

    def test_batch_pauses_unsent_items_after_wallet_error_and_retains_success(self):
        def request(_method, _path, payload, _timeout):
            if payload["keyword"] == "second":
                raise client.ApiError(403, "recharge", "insufficient_user_quota")
            return {"candidateCount": 1}

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "requests.json"
            path.write_text(json.dumps([{"keyword": word} for word in ["first", "second", "third", "fourth"]]))
            output = io.StringIO()
            with patch.object(client, "call_api", side_effect=request) as call:
                with contextlib.redirect_stdout(output):
                    code = client.batch_command(argparse.Namespace(input=str(path), workers=1, timeout=5))
        self.assertEqual(code, 1)
        self.assertEqual(call.call_count, 2)
        items = json.loads(output.getvalue())["results"]
        self.assertEqual(items[0]["result"]["candidateCount"], 1)
        self.assertEqual(items[1]["error"]["code"], "insufficient_user_quota")
        self.assertEqual([item["error"]["code"] for item in items[2:]], ["paused_for_recharge"] * 2)


if __name__ == "__main__":
    unittest.main()
