#!/usr/bin/env python3
"""Daily, anonymous version check. Installation is handled by the host agent."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import ssl
import tempfile
from urllib.request import Request, urlopen

REPOSITORY = "https://github.com/cfanlu/mro-inquiry-match"
SUBDIRECTORY = "skills/mro-inquiry-match"
VERSION_URL = "https://raw.githubusercontent.com/cfanlu/mro-inquiry-match/main/skills/mro-inquiry-match/SKILL.md"


def read_version(text: str) -> tuple[int, int, int]:
    parts = text.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError("Missing Skill frontmatter")
    if not re.search(r"(?m)^name:\s*mro-inquiry-match\s*$", parts[1]):
        raise ValueError("Unexpected Skill name")
    match = re.search(r'''(?m)^\s+version:\s*["']?(\d+\.\d+\.\d+)["']?\s*$''', parts[1])
    if not match:
        raise ValueError("Expected a stable major.minor.patch Skill version")
    return tuple(int(part) for part in match[1].split("."))


def fetch_skill() -> str:
    try:
        import certifi

        context = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        context = ssl.create_default_context()
    # No MRO API credentials or account data are used for this public request.
    request = Request(VERSION_URL, headers={"Cache-Control": "no-cache", "User-Agent": "mro-inquiry-match-update-check"})
    with urlopen(request, timeout=15, context=context) as response:
        data = response.read(256 * 1024 + 1)
    if len(data) > 256 * 1024:
        raise ValueError("Remote Skill document is unexpectedly large")
    return data.decode("utf-8")


def check_update(skill_dir: Path, cache_dir: Path, today: str, force: bool = False) -> dict:
    skill_dir = skill_dir.resolve()
    local = read_version((skill_dir / "SKILL.md").read_text(encoding="utf-8"))
    local_text = ".".join(map(str, local))
    key = hashlib.sha256(str(skill_dir).encode()).hexdigest()[:16]
    state_path = cache_dir / (key + ".json")
    base = {"localVersion": local_text, "repository": REPOSITORY, "skillSubdirectory": SUBDIRECTORY}
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        cached = (
            not force and state["checkedDate"] == today
            and state["skillPath"] == str(skill_dir)
            and local_text in (state["localVersion"], state["remoteVersion"])
            and state["repository"] == REPOSITORY
        )
        remote = tuple(int(part) for part in state["remoteVersion"].split("."))
        if len(remote) != 3:
            cached = False
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        cached = False
    if not cached:
        try:
            remote = read_version(fetch_skill())
        except Exception as error:
            return {**base, "status": "check_failed", "cached": False, "message": "Continue with the installed Skill; the daily check was not recorded as successful.", "errorType": type(error).__name__}
        state = {**base, "skillPath": str(skill_dir), "checkedDate": today, "remoteVersion": ".".join(map(str, remote))}
        temporary = None
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=cache_dir, delete=False) as handle:
                temporary = Path(handle.name)
                json.dump(state, handle, ensure_ascii=False)
            temporary.replace(state_path)
        except OSError:
            return {**base, "status": "update_available" if remote > local else "up_to_date", "remoteVersion": state["remoteVersion"], "cached": False, "warning": "Version checked, but daily cache could not be saved."}
        finally:
            if temporary is not None:
                try:
                    temporary.unlink()
                except OSError:
                    pass
    return {**base, "status": "update_available" if remote > local else "up_to_date", "remoteVersion": ".".join(map(str, remote)), "checkedDate": today, "cached": cached}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--cache-dir", type=Path, default=Path.home() / ".cache" / "mro-inquiry-match" / "updates")
    parser.add_argument("--force", action="store_true", help="Check again even when today's check succeeded")
    args = parser.parse_args()
    try:
        result = check_update(args.skill_dir, args.cache_dir, datetime.now().astimezone().date().isoformat(), args.force)
    except (OSError, ValueError):
        result = {"status": "check_failed", "message": "Cannot read the installed Skill version; continue with the current Skill and report the problem."}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
