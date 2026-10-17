# PHOENIX 15 — publish exact frozen V85 launcher to GitHub
# Run this cell in the SAME Colab that has the frozen Drive checkpoint.
# Requires Colab Secret named GITHUB_TOKEN with Contents: Read and write.
# Creates/updates only phoenix15/colab/PHOENIX15_V85_START_STANDARD.py.
# Never changes the protected V86 entry point, DB, or model.

from pathlib import Path
import base64
import requests

CHECKPOINT = Path(
    "/content/drive/MyDrive/PhoenixTrav/phoenix_15_live/"
    "frozen_runs/PHOENIX15_V85_2026-10-17_20261017_102044"
)
SOURCE = CHECKPOINT / "launcher_cell.py"
REPO = "Travkungen/Travsystem"
TARGET_PATH = "phoenix15/colab/PHOENIX15_V85_START_STANDARD.py"
BRANCH = "main"

if not SOURCE.is_file():
    raise FileNotFoundError(f"Frozen launcher not found: {SOURCE}")

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

code = SOURCE.read_text(encoding="utf-8")
if len(code.strip()) < 100:
    raise RuntimeError("Source looks unexpectedly short; refusing to publish.")
if "V85" not in code.upper() or "PHOENIX" not in code.upper():
    raise RuntimeError("Source does not look like the Phoenix V85 launcher; refusing.")

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
    "message": "feat: publish exact frozen Phoenix 15 V85 launcher",
    "content": base64.b64encode(code.encode("utf-8")).decode("ascii"),
    "branch": BRANCH,
}
if check.status_code == 200:
    payload["sha"] = check.json()["sha"]

response = requests.put(api, headers=headers, json=payload, timeout=30)
if response.status_code not in (200, 201):
    raise RuntimeError(f"GitHub publish failed ({response.status_code}): {response.text[:800]}")

result = response.json()
print("=" * 62)
print("PHOENIX 15 — V85 SOURCE PUBLISHED")
print("=" * 62)
print("Path:", TARGET_PATH)
print("Commit:", result.get("commit", {}).get("sha"))
print("URL:", result.get("content", {}).get("html_url"))
print("Source bytes:", len(code.encode("utf-8")))
print("Protected V86 entry point: untouched")
print("Database/model: untouched")
