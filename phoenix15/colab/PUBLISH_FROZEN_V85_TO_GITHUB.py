# PHOENIX 15 — publish exact frozen V85 launcher to GitHub
# Run this cell in the SAME Colab that has the frozen Drive checkpoint.
# Requires Colab Secret GITHUB_TOKEN with GitHub Contents write access.
# Validates the Drive manifest before publishing, then verifies GitHub copy.
# Changes only phoenix15/colab/PHOENIX15_V85_START_STANDARD.py.
# Never changes the V86 entry point, database, or model.

from pathlib import Path
import base64
import hashlib
import json
import re
import requests

CHECKPOINT = Path(
    "/content/drive/MyDrive/PhoenixTrav/phoenix_15_live/"
    "frozen_runs/PHOENIX15_V85_2026-10-17_20261017_102044"
)
SOURCE = CHECKPOINT / "launcher_cell.py"
MANIFEST_CANDIDATES = [
    CHECKPOINT / "MANIFEST.json",
    CHECKPOINT / "manifest.json",
    CHECKPOINT / "MANIFEST.txt",
    CHECKPOINT / "manifest.txt",
]
REPO = "Travkungen/Travsystem"
TARGET_PATH = "phoenix15/colab/PHOENIX15_V85_START_STANDARD.py"
BRANCH = "main"

if not SOURCE.is_file():
    raise FileNotFoundError(f"Frozen launcher not found: {SOURCE}")

manifest_path = next((p for p in MANIFEST_CANDIDATES if p.is_file()), None)
if manifest_path is None:
    raise FileNotFoundError(
        "Manifest not found. Refusing to publish without source integrity check. "
        "Expected MANIFEST.json or manifest.json (or a text manifest) in the frozen folder."
    )

code_bytes = SOURCE.read_bytes()
actual_sha256 = hashlib.sha256(code_bytes).hexdigest()
manifest_text = manifest_path.read_text(encoding="utf-8")

def collect_hashes(obj, trail=""):
    found = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            next_trail = f"{trail}/{key}"
            key_lower = str(key).lower()
            if isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{64}", value.strip()):
                if "sha256" in key_lower or "sha256" in next_trail.lower():
                    found.append((next_trail, value.strip().lower()))
            found.extend(collect_hashes(value, next_trail))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            found.extend(collect_hashes(value, f"{trail}/{i}"))
    return found

expected_hash = None
try:
    manifest_obj = json.loads(manifest_text)
    candidates = collect_hashes(manifest_obj)
    # Prefer a manifest entry explicitly referring to launcher_cell.py.
    source_matches = [(p, h) for p, h in candidates if "launcher_cell.py" in p.lower()]
    if len(source_matches) == 1:
        expected_hash = source_matches[0][1]
    elif len(candidates) == 1:
        expected_hash = candidates[0][1]
except json.JSONDecodeError:
    # Text-manifest fallback: require the launcher filename and a SHA-256 value
    # to appear on the same line; fail closed if ambiguous.
    for line in manifest_text.splitlines():
        if "launcher_cell.py" in line.lower():
            hashes = re.findall(r"(?i)(?:sha256\s*[:=]\s*)?([0-9a-f]{64})", line)
            if len(hashes) == 1:
                expected_hash = hashes[0].lower()
                break

if not expected_hash:
    raise RuntimeError(
        f"Could not identify an unambiguous SHA-256 for launcher_cell.py in {manifest_path.name}. "
        "No file has been published. Inspect the manifest before proceeding."
    )
if actual_sha256 != expected_hash:
    raise RuntimeError(
        "FROZEN SOURCE CHECK FAILED — refusing to publish. "
        f"Manifest SHA-256={expected_hash}; actual SHA-256={actual_sha256}"
    )

code = code_bytes.decode("utf-8")
if len(code.strip()) < 100:
    raise RuntimeError("Source looks unexpectedly short; refusing to publish.")
if "V85" not in code.upper() or "PHOENIX" not in code.upper():
    raise RuntimeError("Source does not look like the Phoenix V85 launcher; refusing.")

try:
    from google.colab import userdata
    token = userdata.get("GITHUB_TOKEN")
except Exception as e:
    raise RuntimeError(
        "Add a Colab Secret named GITHUB_TOKEN with GitHub Contents write access, "
        "then run this cell again."
    ) from e

if not token:
    raise RuntimeError("Colab Secret GITHUB_TOKEN is empty or unavailable.")

api = f"https://api.github.com/repos/{REPO}/contents/{TARGET_PATH}"
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
check = requests.get(api, headers=headers, params={"ref": BRANCH}, timeout=30)
if check.status_code not in (200, 404):
    raise RuntimeError(f"GitHub read failed ({check.status_code}): {check.text[:500]}")

payload = {
    "message": "feat: publish verified frozen Phoenix 15 V85 launcher",
    "content": base64.b64encode(code_bytes).decode("ascii"),
    "branch": BRANCH,
}
if check.status_code == 200:
    payload["sha"] = check.json()["sha"]

response = requests.put(api, headers=headers, json=payload, timeout=30)
if response.status_code not in (200, 201):
    raise RuntimeError(f"GitHub publish failed ({response.status_code}): {response.text[:800]}")

# Read the committed file back and verify its exact SHA-256.
verify = requests.get(api, headers=headers, params={"ref": BRANCH}, timeout=30)
if verify.status_code != 200:
    raise RuntimeError(f"Publish succeeded but read-back failed ({verify.status_code}).")
github_bytes = base64.b64decode(verify.json()["content"])
github_sha256 = hashlib.sha256(github_bytes).hexdigest()
if github_sha256 != actual_sha256:
    raise RuntimeError(
        "GitHub read-back SHA-256 mismatch. Do not use the published file. "
        f"Drive={actual_sha256}; GitHub={github_sha256}"
    )

result = response.json()
print("=" * 62)
print("PHOENIX 15 — VERIFIED V85 SOURCE PUBLISHED")
print("=" * 62)
print("Path:", TARGET_PATH)
print("Commit:", result.get("commit", {}).get("sha"))
print("URL:", result.get("content", {}).get("html_url"))
print("Source bytes:", len(code_bytes))
print("SHA-256:", actual_sha256)
print("Manifest validation: PASS")
print("GitHub read-back validation: PASS")
print("Protected V86 entry point: untouched")
print("Database/model: untouched")
