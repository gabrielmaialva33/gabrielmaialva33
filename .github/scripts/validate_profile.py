#!/usr/bin/env python3
"""Repository-local checks for the GitHub profile and its automation."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
WORKFLOWS = ROOT / ".github" / "workflows"
EXPECTED_TELEGRAM_URL = "https://t.me/sr_mrootx"
EXPECTED_3D_ASSETS = {"profile-night-rainbow.svg"}
SHA_PATTERN = re.compile(r"[0-9a-f]{40}")

errors: list[str] = []


def report(message: str) -> None:
    errors.append(message)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        report(f"Unable to read {path.relative_to(ROOT)}: {exc}")
        return ""


readme = read_text(README)

if readme.count("<!--START_SECTION:waka-->") != 1:
    report("README.md must contain exactly one WakaTime start marker.")
if readme.count("<!--END_SECTION:waka-->") != 1:
    report("README.md must contain exactly one WakaTime end marker.")

if len(readme.splitlines()) > 520:
    report("README.md exceeded the 520-line maintainability budget.")

image_sources = re.findall(r'<img\b[^>]*\bsrc=["\']([^"\']+)', readme, re.IGNORECASE)
image_sources.extend(re.findall(r"!\[[^\]]*\]\(([^)\s]+)", readme))

if len(image_sources) > 50:
    report(f"README.md contains {len(image_sources)} images; the limit is 50.")

for source in image_sources:
    if not source.startswith(("./", "../")):
        continue

    clean_source = source.split("#", 1)[0].split("?", 1)[0]
    target = (ROOT / clean_source).resolve()

    try:
        target.relative_to(ROOT.resolve())
    except ValueError:
        report(f"Local image escapes the repository: {source}")
        continue

    if not target.is_file():
        report(f"Local image does not exist: {source}")

telegram_urls = set(re.findall(r"https://t\.me/[^\s\"'<>)]+", readme))
if telegram_urls != {EXPECTED_TELEGRAM_URL}:
    report(
        "Telegram links must be consistent. "
        f"Expected only {EXPECTED_TELEGRAM_URL}, found {sorted(telegram_urls)}."
    )

for forbidden in (
    "AI Code Time",
    "AI Coding This Week",
    "Estimated AI Cost",
    "Input Tokens",
    "AI-written",
    "sr__mrootx",
    "https://t.me/mrootx",
):
    if forbidden in readme:
        report(f"README.md contains forbidden or stale content: {forbidden!r}.")

profile_assets_dir = ROOT / "profile-3d-contrib"
actual_3d_assets = {path.name for path in profile_assets_dir.glob("*.svg")}
if actual_3d_assets != EXPECTED_3D_ASSETS:
    report(
        "Only the published 3D calendar should be tracked. "
        f"Expected {sorted(EXPECTED_3D_ASSETS)}, found {sorted(actual_3d_assets)}."
    )

if (ROOT / "assets").exists():
    report("The unused assets/ directory should not be tracked.")

workflow_files = sorted(WORKFLOWS.glob("*.yml")) + sorted(WORKFLOWS.glob("*.yaml"))
if not workflow_files:
    report("No GitHub Actions workflows were found.")

uses_pattern = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)", re.MULTILINE)
for workflow in workflow_files:
    content = read_text(workflow)
    for match in uses_pattern.finditer(content):
        action = match.group(1)
        if action.startswith(("./", "docker://")):
            continue
        if "@" not in action:
            report(f"{workflow.name}: action has no revision: {action}")
            continue
        reference = action.rsplit("@", 1)[1]
        if not SHA_PATTERN.fullmatch(reference):
            report(f"{workflow.name}: action is not pinned to a full commit SHA: {action}")

profile_workflow = read_text(WORKFLOWS / "profile-3d.yml")
snake_workflow = read_text(WORKFLOWS / "snake.yml")
stats_workflow = read_text(WORKFLOWS / "update-stats.yml")

for name, content in (
    ("profile-3d.yml", profile_workflow),
    ("snake.yml", snake_workflow),
):
    if "secrets.GH_TOKEN" in content:
        report(f"{name} must use the workflow-scoped GitHub token, not the personal token.")

for required_setting in (
    'PUSH_TOKEN: ${{ github.token }}',
    'SHOW_AI_CODE_TIME: "False"',
    'SHOW_AI_CODING: "False"',
    'SHOW_LINES_OF_CODE: "False"',
    'SHOW_EDITORS: "False"',
):
    if required_setting not in stats_workflow:
        report(f"update-stats.yml is missing required hardening setting: {required_setting}")

if errors:
    print("Profile validation failed:", file=sys.stderr)
    for error in errors:
        print(f"  - {error}", file=sys.stderr)
    raise SystemExit(1)

print(
    "Profile validation passed: "
    f"{len(readme.splitlines())} README lines, "
    f"{len(image_sources)} images, "
    f"{len(workflow_files)} workflows."
)
